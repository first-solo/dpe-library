#!/usr/bin/env python3
"""Keep a tracked copy of a document that cannot be re-fetched from a URL.

    python scripts/mirror.py add <id> <file.pdf>

Copies the file to mirror/<id>.pdf, and sets `mirror: true` and `sha256` on
the catalog entry. Everything else in the entry is left as it was.

This is for documents with no stable direct download: DRS exports above all
(8900.1 sections, 8000.95), plus superseded PTSs and legal interpretations.
Anything fetch.py can pull from a verified pdf_url stays out of the repo; a
document the owner supplies with no recorded link is mirrored instead of
leaving pdf_url as a TODO.

Replacing a copy is allowed and expected when a new change is published; the
old one stays in git history. `build.py --check` fails if a mirrored file no
longer matches its recorded sha256, or if a file in mirror/ has no entry.
"""

from __future__ import annotations

import argparse
import pathlib
import shutil
import sys

import dpelib as L
from catalog_writer import write_fields


def add(doc_id: str, src: str) -> int:
    ids = {d.get("id") for d in L.load_catalog(private=False)}
    if doc_id not in ids:
        print(f"  no catalog entry '{doc_id}'", file=sys.stderr)
        return 1

    src_path = pathlib.Path(src)
    head = src_path.read_bytes()[:5]
    if head != b"%PDF-":
        print(f"  {src} is not a PDF", file=sys.stderr)
        return 1

    dest = L.MIRROR / f"{doc_id}.pdf"
    digest = L.sha256_file(src_path)
    if dest.exists():
        old = L.sha256_file(dest)
        if old == digest:
            print(f"  same  {doc_id}  {digest[:12]}")
        else:
            print(f"  repl  {doc_id}  {old[:12]} -> {digest[:12]}")
    else:
        print(f"  new   {doc_id}  {digest[:12]}")

    L.MIRROR.mkdir(exist_ok=True)
    shutil.copyfile(src_path, dest)
    write_fields(doc_id, {"mirror": True, "sha256": digest})
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="copy a file into mirror/ and record it")
    a.add_argument("id")
    a.add_argument("file")
    args = ap.parse_args()
    return add(args.id, args.file)


if __name__ == "__main__":
    sys.exit(main())
