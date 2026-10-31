#!/usr/bin/env python3
"""Confirm mirror.py records a copy and build validation holds it to its hash.

    PYTHONPATH=scripts python tests/test_mirror.py

Runs against a throwaway catalog and mirror/; the real ones are not touched.
"""

from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import dpelib as L
import mirror as M

ENTRY = """\
id: doc-a
title: A document   # keep this comment
type: order
status: current
source_url: https://drs.faa.gov/browse
pdf_url:            # DRS export, no direct link
mirror: false
tags: [x]
"""

failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="dpe-mirror-"))
    try:
        (tmp / "catalog").mkdir()
        (tmp / "catalog" / "doc-a.yaml").write_text(ENTRY)
        src = tmp / "export.pdf"
        src.write_bytes(b"%PDF-1.7\nfirst\n")
        L.CATALOG, L.MIRROR = tmp / "catalog", tmp / "mirror"

        check(M.add("doc-a", str(src)) == 0, "add succeeds")
        text = (tmp / "catalog" / "doc-a.yaml").read_text()
        check("mirror: true" in text, "mirror set true")
        check(f"sha256: {L.sha256_file(src)}" in text, "sha256 recorded")
        check("# keep this comment" in text and "# DRS export" in text,
              "comments preserved")
        errors, _ = L.validate(L.load_catalog())
        check(not errors, "valid after add")
        check(L.doc_link(L.load_catalog()[0]) == "mirror/doc-a.pdf",
              "links to the mirror copy")

        (tmp / "mirror" / "doc-a.pdf").write_bytes(b"%PDF-1.7\nedited\n")
        errors, _ = L.validate(L.load_catalog())
        check(any("does not match" in e for e in errors), "edited copy fails")

        src.write_bytes(b"%PDF-1.7\nsecond\n")
        M.add("doc-a", str(src))
        errors, _ = L.validate(L.load_catalog())
        check(not errors, "replacing a copy re-records its hash")

        (tmp / "mirror" / "stray.pdf").write_bytes(b"%PDF-1.7\n")
        errors, _ = L.validate(L.load_catalog())
        check(any("stray.pdf" in e for e in errors), "unclaimed file fails")

        bad = tmp / "page.html"
        bad.write_text("<html>")
        check(M.add("doc-a", str(bad)) == 1, "non-PDF refused")
        check(M.add("no-such-id", str(src)) == 1, "unknown id refused")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nall checks passed" if not failures else f"\n{len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
