#!/usr/bin/env python3
"""Generate the table of contents and search index from the catalog.

Public artifacts (tracked, published):
    README.md
    site/index.json

Private artifacts (gitignored, yours only):
    local/README.private.md
    local/index.json

There is deliberately no flag that writes private content to a tracked path.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

import dpelib as L

STATUS_MARK = {
    "current": "",
    "superseded": " *(superseded)*",
    "historical": " *(historical)*",
    "unknown": " *(status unverified)*",
}

TYPE_LABEL = {
    "order": "Orders",
    "notice": "Notices",
    "ac": "Advisory Circulars",
    "acs": "Airman Certification Standards",
    "pts": "Practical Test Standards",
    "handbook": "Handbooks",
    "interpretation": "Legal Interpretations",
    "policy": "Policy",
    "cfr": "Regulations",
    "other": "Other",
}


def entry_line(d: dict, show_private: bool) -> list[str]:
    url = L.doc_link(d)
    title = d.get("title", d.get("id"))
    label = f"[{title}]({url})" if url else title

    bits = []
    if d.get("doc_number"):
        bits.append(f"`{d['doc_number']}`")
    if d.get("revision"):
        bits.append(f"Rev {d['revision']}")
    if d.get("effective_date"):
        bits.append(str(d["effective_date"]))
    meta = " · ".join(bits)

    lines = [f"- {label}{STATUS_MARK.get(d.get('status'), '')}"]
    if meta:
        lines.append(f"  {meta}")
    if d.get("tags"):
        lines.append("  " + " ".join(f"`{t}`" for t in d["tags"]))
    if d.get("notes"):
        for para in str(d["notes"]).strip().splitlines():
            if para.strip():
                lines.append(f"  > {para.strip()}")
    if show_private and d.get("private_notes"):
        for para in str(d["private_notes"]).strip().splitlines():
            if para.strip():
                lines.append(f"  🔒 {para.strip()}")
    if d.get("related"):
        lines.append("  See also: " + ", ".join(f"`{r}`" for r in d["related"]))
    return lines


def render_readme(docs: list[dict], show_private: bool, todos: list[str]) -> str:
    stamp = dt.date.today().isoformat()
    out = [
        "# DPE Reference Library",
        "",
        "Curated index of FAA guidance used for practical tests. The PDFs are not",
        "stored here; each entry links to the FAA source. Run `make fetch` to pull",
        "local copies into `local/`.",
        "",
        "**Nothing in this repository is authoritative.** Always confirm currency",
        "against the FAA source before relying on a document.",
        "",
        f"Generated {stamp} · {len(docs)} documents",
        "",
    ]

    if show_private:
        private_count = sum(1 for d in docs if d.get("_has_private"))
        out += [
            f"> Private view. {private_count} entries carry overlay content marked 🔒.",
            "> This file lives in `local/` and is gitignored.",
            "",
        ]

    grouped = L.by_type(docs)
    out += ["## Contents", ""]
    for key in TYPE_LABEL:
        if key in grouped:
            out.append(f"- [{TYPE_LABEL[key]}](#{TYPE_LABEL[key].lower().replace(' ', '-')})")
    out += ["- [By certificate](#by-certificate)", "- [By tag](#by-tag)", ""]

    for key, label in TYPE_LABEL.items():
        if key not in grouped:
            continue
        out += [f"## {label}", ""]
        for d in grouped[key]:
            out += entry_line(d, show_private)
            out.append("")

    out += ["## By certificate", ""]
    for cert, items in L.applies_index(docs).items():
        names = ", ".join(f"[{d.get('title')}]({L.doc_link(d)})" for d in items)
        out.append(f"- **{cert}** — {names}")
    out.append("")

    out += ["## By tag", ""]
    for tag, items in L.tag_index(docs).items():
        names = ", ".join(f"[{d.get('title')}]({L.doc_link(d)})" for d in items)
        out.append(f"- `{tag}` — {names}")
    out.append("")

    if todos:
        out += ["## Needs verification", ""]
        out += [f"- {t}" for t in todos]
        out.append("")

    return "\n".join(out)


def search_index(docs: list[dict], show_private: bool) -> list[dict]:
    rows = []
    for d in docs:
        row = {
            "id": d.get("id"),
            "title": d.get("title"),
            "doc_number": d.get("doc_number"),
            "type": d.get("type"),
            "status": d.get("status"),
            "revision": d.get("revision"),
            "effective_date": str(d.get("effective_date") or ""),
            "url": L.doc_link(d),
            "tags": d.get("tags") or [],
            "applies_to": d.get("applies_to") or [],
            "notes": d.get("notes") or "",
            "related": d.get("related") or [],
        }
        if show_private:
            row["private_notes"] = d.get("private_notes") or ""
        rows.append(row)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="validate and confirm tracked output is current; write nothing")
    args = ap.parse_args()

    public = L.load_catalog(private=False)
    errors, todos = L.validate(public)
    for e in errors:
        print(f"  error: {e}", file=sys.stderr)
    if errors:
        print(f"\n{len(errors)} validation error(s).", file=sys.stderr)
        return 1

    readme = render_readme(public, show_private=False, todos=todos)
    index = json.dumps(search_index(public, show_private=False), indent=2)

    if args.check:
        stale = []
        if (L.ROOT / "README.md").read_text() != readme:
            stale.append("README.md")
        site_index = L.SITE / "index.json"
        if not site_index.exists() or site_index.read_text() != index:
            stale.append("site/index.json")
        if stale:
            print(f"Stale generated files: {', '.join(stale)}. Run `make build`.",
                  file=sys.stderr)
            return 1
        print(f"ok — {len(public)} documents, {len(todos)} needing verification")
        return 0

    (L.ROOT / "README.md").write_text(readme)
    L.SITE.mkdir(exist_ok=True)
    (L.SITE / "index.json").write_text(index)
    print(f"public  → README.md, site/index.json ({len(public)} documents)")

    merged = L.load_catalog(private=True)
    L.LOCAL.mkdir(exist_ok=True)
    (L.LOCAL / "README.private.md").write_text(
        render_readme(merged, show_private=True, todos=todos)
    )
    (L.LOCAL / "index.json").write_text(
        json.dumps(search_index(merged, show_private=True), indent=2)
    )
    overlaid = sum(1 for d in merged if d.get("_has_private"))
    print(f"private → local/README.private.md, local/index.json ({overlaid} with overlay)")

    if todos:
        print(f"\n{len(todos)} field(s) need verification:")
        for t in todos:
            print(f"  - {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
