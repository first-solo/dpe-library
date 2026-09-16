"""Shared catalog handling for the DPE reference library.

Two hard rules live in this file:

1. load_catalog(private=False) NEVER touches private/. Anything written to a
   tracked path in the repo must be built from that call.
2. The private overlay is merged on top of the public record, key by key. The
   public record is never mutated in place.
"""

from __future__ import annotations

import copy
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
PRIVATE = ROOT / "private"
SITE = ROOT / "site"
LOCAL = ROOT / "local"

# Fields every entry must carry. TODO is tolerated and reported, not fatal,
# so you can stub an entry now and verify the volatile fields later.
REQUIRED = ["id", "title", "type", "status", "source_url", "tags"]

TYPES = [
    "order", "notice", "ac", "acs", "pts", "handbook",
    "interpretation", "policy", "cfr", "other",
]

STATUSES = ["current", "superseded", "historical", "unknown"]

ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


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

        for key, val in d.items():
            if isinstance(val, str) and "TODO" in val:
                todos.append(f"{name}: {key} needs verification")

    return errors, todos


def warn(msg: str) -> None:
    print(f"  warn: {msg}", file=sys.stderr)


def by_type(docs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in docs:
        out.setdefault(d.get("type", "other"), []).append(d)
    for v in out.values():
        v.sort(key=lambda d: d.get("title", ""))
    return out


def tag_index(docs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in docs:
        for tag in d.get("tags") or []:
            out.setdefault(tag, []).append(d)
    return dict(sorted(out.items()))


def applies_index(docs: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for d in docs:
        for cert in d.get("applies_to") or []:
            out.setdefault(cert, []).append(d)
    return dict(sorted(out.items()))


def doc_link(d: dict) -> str:
    """Prefer the direct file, fall back to the landing page."""
    return d.get("pdf_url") or d.get("source_url") or ""
