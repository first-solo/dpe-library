"""Shared catalog handling for the DPE reference library.

Two hard rules live in this file:

1. load_catalog(private=False) NEVER touches private/. Anything written to a
   tracked path in the repo must be built from that call.
2. The private overlay is merged on top of the public record, key by key. The
   public record is never mutated in place.
"""

from __future__ import annotations

import copy
import hashlib
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
PRIVATE = ROOT / "private"
SITE = ROOT / "site"
LOCAL = ROOT / "local"
MIRROR = ROOT / "mirror"

# Fields every entry must carry. TODO is tolerated and reported, not fatal,
# so you can stub an entry now and verify the volatile fields later.
REQUIRED = ["id", "title", "type", "status", "source_url", "tags"]

TYPES = [
    "order", "notice", "ac", "acs", "pts", "handbook",
    "interpretation", "policy", "cfr", "other",
]

STATUSES = ["current", "superseded", "historical", "unknown"]

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# A 14 CFR citation in `interprets:`. Part.section, then any paragraph
# designators: 61.51(e)(1)(i), 1.1, 91.213(d)(2). Appendices have no section
# number, so they are written as "141 Appendix B". No "14 CFR" prefix and no
# "§": every entry is Title 14, and the prefix only invites inconsistency.
CFR_RE = re.compile(r"^(\d+\.\d+[a-z]?(\([a-zA-Z0-9]+\))*|\d+ Appendix [A-Z]+)$")


def _deep_merge(base: dict, over: dict) -> dict:
    """Overlay wins. Dicts merge recursively; lists and scalars replace.

    Exception: keys ending in _append have their list concatenated onto the
    base key of the same name, so private files can add tags without
    restating the public ones.
    """
    out = copy.deepcopy(base)
    for k, v in over.items():
        if k.endswith("_append"):
            target = k[: -len("_append")]
            out.setdefault(target, [])
            out[target] = list(out[target]) + list(v)
        elif isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_catalog(private: bool = False) -> list[dict]:
    """Load every catalog entry. Set private=True only for gitignored output."""
    docs = []
    for path in sorted(CATALOG.glob("*.yaml")):
        with path.open() as fh:
            doc = yaml.safe_load(fh) or {}
        doc["_file"] = path.name
        doc["_private_fields"] = []

        if doc.get("id") != path.stem:
            warn(f"{path.name}: id '{doc.get('id')}' does not match filename stem")

        if private:
            overlay_path = PRIVATE / path.name
            if overlay_path.exists():
                with overlay_path.open() as fh:
                    overlay = yaml.safe_load(fh) or {}
                overlay.pop("id", None)  # id is public and immutable
                doc["_private_fields"] = sorted(overlay.keys())
                doc = _deep_merge(doc, overlay)
                doc["_has_private"] = True

        docs.append(doc)
    return docs


def validate(docs: list[dict]) -> tuple[list[str], list[str]]:
    """Return (errors, todos). Errors are fatal, todos are reported."""
    errors, todos = [], []
    ids = {d.get("id") for d in docs}

    for d in docs:
        name = d.get("_file", "?")

        for field in REQUIRED:
            if field not in d or d[field] in (None, "", []):
                errors.append(f"{name}: missing required field '{field}'")

        did = d.get("id", "")
        if did and not ID_RE.match(did):
            errors.append(f"{name}: id '{did}' should be lowercase-hyphenated")

        if d.get("type") not in TYPES:
            errors.append(f"{name}: type '{d.get('type')}' not in {TYPES}")

        if d.get("status") not in STATUSES:
            errors.append(f"{name}: status '{d.get('status')}' not in {STATUSES}")

        for field in ("related", "supersedes", "superseded_by"):
            for ref in d.get(field) or []:
                if ref not in ids:
                    errors.append(f"{name}: {field} points at unknown id '{ref}'")

        interprets = d.get("interprets")
        if interprets is not None:
            if not isinstance(interprets, list):
                errors.append(f"{name}: interprets must be a list")
            else:
                for ref in interprets:
                    if not CFR_RE.match(str(ref)):
                        errors.append(
                            f"{name}: interprets entry '{ref}' is not a 14 CFR "
                            "citation like 61.51(e)(1)(i)"
                        )

        for key, val in d.items():
            if isinstance(val, str) and "TODO" in val:
                todos.append(f"{name}: {key} needs verification")

        if d.get("mirror"):
            copy_path = mirror_path(d)
            if not copy_path.exists():
                todos.append(f"{name}: mirror is true but mirror/{copy_path.name} is missing")
            elif not d.get("sha256"):
                errors.append(f"{name}: mirror/{copy_path.name} has no sha256 in the catalog")
            elif sha256_file(copy_path) != d["sha256"]:
                errors.append(f"{name}: mirror/{copy_path.name} does not match its catalog sha256")

    # A copy with no entry claiming it is either a typo or a leftover.
    if MIRROR.exists():
        claimed = {mirror_path(d).name for d in docs if d.get("mirror")}
        for f in sorted(MIRROR.iterdir()):
            if f.is_file() and f.name not in claimed:
                errors.append(f"mirror/{f.name}: no catalog entry with mirror: true claims it")

    return errors, todos


def mirror_path(d: dict) -> pathlib.Path:
    return MIRROR / f"{d.get('id')}.pdf"


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warn(msg: str) -> None:
    print(f"  warn: {msg}", file=sys.stderr)


def by_type(docs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in docs:
        out.setdefault(d.get("type", "other"), []).append(d)
    for v in out.values():
        v.sort(key=lambda d: _natural_key(d.get("title", "")))
    return out


def _natural_key(text: str) -> list:
    """Sort "Sec 2" before "Sec 11" without disturbing plain titles."""
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", text)]


def tag_index(docs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in docs:
        for tag in d.get("tags") or []:
            out.setdefault(tag, []).append(d)
    return dict(sorted(out.items()))


def cfr_section(ref: str) -> str:
    """61.51(e)(1)(i) -> 61.51. Appendix citations are their own section."""
    return str(ref).split("(", 1)[0]


def _cfr_sort_key(section: str) -> tuple:
    head = section.split(" ", 1)[0]
    part, _, sec = head.partition(".")
    num = re.match(r"\d+", sec or "")
    return (int(part), sec == "", int(num.group()) if num else 0, section)


def regulation_index(docs: list[dict]) -> dict[str, list[tuple[dict, list[str]]]]:
    """Section -> [(doc, [the paragraphs it cites in that section])].

    Grouped at section level (61.51, not 61.51(e)(1)(i)) because that is how
    you look something up; the paragraphs ride along so the index still says
    which part of the section a letter is about.
    """
    out: dict[str, dict[str, tuple[dict, list[str]]]] = {}
    for d in docs:
        for ref in d.get("interprets") or []:
            sec = cfr_section(ref)
            bucket = out.setdefault(sec, {})
            entry = bucket.setdefault(d["id"], (d, []))
            if str(ref) != sec:
                entry[1].append(str(ref))
    result = {}
    for sec in sorted(out, key=_cfr_sort_key):
        items = sorted(out[sec].values(),
                       key=lambda e: (str(e[0].get("effective_date") or ""), e[0]["id"]))
        result[sec] = items
    return result


def applies_index(docs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in docs:
        for cert in d.get("applies_to") or []:
            out.setdefault(cert, []).append(d)
    return dict(sorted(out.items()))


def doc_link(d: dict) -> str:
    """Prefer the direct file, then the tracked mirror copy, then the landing page.

    The mirror link is repo-relative, so it resolves from README.md on GitHub.
    A stubbed `TODO` is not a link; skip it rather than rendering one.
    """
    val = d.get("pdf_url")
    if val and "TODO" not in str(val):
        return val
    if d.get("mirror") and mirror_path(d).exists():
        return f"mirror/{mirror_path(d).name}"
    val = d.get("source_url")
    if val and "TODO" not in str(val):
        return val
    return ""
