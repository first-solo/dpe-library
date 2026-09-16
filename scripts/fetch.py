#!/usr/bin/env python3
"""Download local copies of catalogued PDFs into local/pdfs/ (gitignored).

Entries with `mirror: true` are additionally copied into mirror/, which IS
tracked, for documents that are hard to find upstream (superseded PTSs,
pulled interpretations).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import urllib.error
import urllib.request

import dpelib as L

UA = "dpe-library/0.1 (personal reference index)"


def download(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="fetch a single document id")
    ap.add_argument("--force", action="store_true", help="re-download existing files")
    args = ap.parse_args()

    docs = L.load_catalog(private=False)
    outdir = L.LOCAL / "pdfs"
    outdir.mkdir(parents=True, exist_ok=True)
    mirrordir = L.ROOT / "mirror"

    fetched = skipped = failed = 0
    for d in docs:
        if args.only and d.get("id") != args.only:
            continue
        url = d.get("pdf_url")
        if not url or "TODO" in str(url):
            print(f"  skip  {d['id']} (no direct pdf_url)")
            skipped += 1
            continue

        dest = outdir / f"{d['id']}.pdf"
        if dest.exists() and not args.force:
            print(f"  have  {d['id']}")
            skipped += 1
            continue

        try:
            body = download(url)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            print(f"  FAIL  {d['id']}: {exc}", file=sys.stderr)
            failed += 1
            continue

        dest.write_bytes(body)
        digest = hashlib.sha256(body).hexdigest()
        note = ""
        if d.get("sha256") and d["sha256"] != digest:
            note = "  << differs from catalog sha256, run check_updates"
        print(f"  got   {d['id']}  {len(body)//1024} KB  {digest[:12]}{note}")
        fetched += 1

        if d.get("mirror"):
            mirrordir.mkdir(exist_ok=True)
            (mirrordir / f"{d['id']}.pdf").write_bytes(body)
            print(f"        mirrored to mirror/{d['id']}.pdf (tracked)")

    print(f"\n{fetched} fetched, {skipped} skipped, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
