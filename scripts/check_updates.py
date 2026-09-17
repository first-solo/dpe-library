#!/usr/bin/env python3
"""Check catalogued documents against their upstream source.

Each entry declares how it should be checked:

    check:
      method: head | hash | scrape | list | manual
      url: <defaults to pdf_url, or source_url for scrape/list>
      pattern: <regex with one capture group, for scrape and list>

  head    compare ETag / Last-Modified / Content-Length against stored values
  hash    download and compare sha256 (use when headers are unreliable)
  scrape  pull a revision string off a landing page and compare to `revision`
  list    count regex matches on an index page and compare to `seen_count`
          (catches new legal interpretations appearing in a yearly list)
  manual  never checked automatically, reported so it stays visible

Exit code 0 means nothing changed. 2 means something did, which is what the
scheduled workflow keys on when deciding whether to open an issue.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request

from ruamel.yaml import YAML

import dpelib as L

UA = "dpe-library/0.1 (personal reference index)"
TIMEOUT = 45

# Round-trip YAML, used only for writing. Catalog files carry `# verify this`
# annotations during backfill, and a safe_load/safe_dump round-trip strips
# every one of them without a word — along with reflowing block scalars and
# turning empty values into explicit nulls. dpelib stays on PyYAML; it only
# reads.
#
# The settings are not cosmetic. Each was checked against the real catalog:
#   preserve_quotes  keeps '([0-9]{4}-[0-9]+)' quoted, since an unquoted regex
#                    starting with a YAML indicator would not survive.
#   indent(2, 2, 0)  matches what is on disk, so untouched list lines do not
#                    move. ruamel sets sequence indent globally at dump time
#                    rather than preserving it per file, so this has to agree
#                    with the repo's style.
#   width            defaults to 80, which wraps a long source_url onto a
#                    continuation line. Catalog URLs routinely exceed that.
_writer = YAML()
_writer.preserve_quotes = True
_writer.indent(mapping=2, sequence=2, offset=0)
_writer.width = 4096


def _open(url: str, method: str = "GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method=method)
    return urllib.request.urlopen(req, timeout=TIMEOUT)


def check_head(d: dict, url: str) -> tuple[str, dict]:
    with _open(url, "HEAD") as r:
        seen = {
            "etag": r.headers.get("ETag", ""),
            "last_modified": r.headers.get("Last-Modified", ""),
            "content_length": r.headers.get("Content-Length", ""),
        }
    stored = d.get("http") or {}
    if not stored:
        return "baseline", {"http": seen}
    changed = [k for k, v in seen.items() if v and stored.get(k) and stored[k] != v]
    if changed:
        return f"CHANGED ({', '.join(changed)})", {"http": seen}
    return "unchanged", {}


def check_hash(d: dict, url: str) -> tuple[str, dict]:
    with _open(url) as r:
        body = r.read()
    digest = hashlib.sha256(body).hexdigest()
    if not d.get("sha256"):
        return f"baseline {digest[:12]}", {"sha256": digest}
    if d["sha256"] != digest:
        return f"CHANGED {d['sha256'][:12]} -> {digest[:12]}", {"sha256": digest}
    return "unchanged", {}


def check_scrape(d: dict, url: str, pattern: str) -> tuple[str, dict]:
    with _open(url) as r:
        html = r.read().decode("utf-8", "replace")
    matches = re.findall(pattern, html)
    if not matches:
        return "PATTERN MISSED (source layout may have changed)", {}
    found = matches[0]
    if str(d.get("revision", "")).strip() != str(found).strip():
        return f"CHANGED revision {d.get('revision')} -> {found}", {}
    return f"unchanged (rev {found})", {}


def check_list(d: dict, url: str, pattern: str) -> tuple[str, dict]:
    with _open(url) as r:
        html = r.read().decode("utf-8", "replace")
    count = len(set(re.findall(pattern, html)))
    prev = (d.get("check") or {}).get("seen_count")
    if prev is None:
        return f"baseline {count} entries", {"check": {"seen_count": count}}
    if count != prev:
        return f"CHANGED {prev} -> {count} entries", {"check": {"seen_count": count}}
    return f"unchanged ({count} entries)", {}


def apply_updates(doc_id: str, updates: dict) -> None:
    """Write the new values back into the catalog file, preserving the rest.

    The write surface is exactly `http`, `sha256`, `check.seen_count` and
    `last_checked`. Every other byte of the file — comments, key order,
    quoting, block scalars, empty values — comes out unchanged. See
    tests/test_apply_updates.py, which fails if that stops being true.
    """
    path = L.CATALOG / f"{doc_id}.yaml"
    with path.open() as fh:
        data = _writer.load(fh) or {}

    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            # Merge into the existing node rather than replacing it, so a
            # comment sitting on a sibling key survives.
            data[k].update(v)
        else:
            data[k] = v

    # Stays a string. Written unquoted it would parse back as a datetime.date,
    # which json.dumps refuses when build.py writes site/index.json — ruamel
    # quotes date-shaped strings on its own, which is what keeps that honest.
    data["last_checked"] = dt.date.today().isoformat()

    with path.open("w") as fh:
        _writer.dump(data, fh)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="write new hashes/headers and last_checked back to the catalog")
    ap.add_argument("--only", help="check a single document id")
    ap.add_argument("--json", help="write a machine-readable report here")
    args = ap.parse_args()

    docs = L.load_catalog(private=False)
    report, changed = [], 0

    for d in docs:
        if args.only and d["id"] != args.only:
            continue
        cfg = d.get("check") or {}
        method = cfg.get("method", "manual")
        url = cfg.get("url") or (
            d.get("source_url") if method in ("scrape", "list") else d.get("pdf_url")
        )

        if method == "manual" or not url or "TODO" in str(url):
            status, updates = "manual — check by hand", {}
        else:
            try:
                if method == "head":
                    status, updates = check_head(d, url)
                elif method == "hash":
                    status, updates = check_hash(d, url)
                elif method == "scrape":
                    status, updates = check_scrape(d, url, cfg["pattern"])
                elif method == "list":
                    status, updates = check_list(d, url, cfg["pattern"])
                else:
                    status, updates = f"unknown method '{method}'", {}
            except (urllib.error.URLError, urllib.error.HTTPError,
                    TimeoutError, KeyError) as exc:
                status, updates = f"ERROR {exc}", {}

        flagged = status.startswith(("CHANGED", "PATTERN MISSED", "ERROR"))
        changed += flagged
        print(f"  {'!!' if flagged else '  '} {d['id']:<34} {status}")
        report.append({"id": d["id"], "title": d.get("title"),
                       "method": method, "status": status, "flagged": flagged})

        if args.write and updates:
            apply_updates(d["id"], updates)

    if args.json:
        L.LOCAL.mkdir(exist_ok=True)
        (L.ROOT / args.json).write_text(json.dumps(report, indent=2))

    print(f"\n{changed} of {len(report)} entries need attention")
    return 2 if changed else 0


if __name__ == "__main__":
    sys.exit(main())
