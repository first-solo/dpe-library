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

import yaml

import dpelib as L

UA = "dpe-library/0.1 (personal reference index)"
TIMEOUT = 45


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
    """Write the new values back into the catalog file, preserving the rest."""
    path = L.CATALOG / f"{doc_id}.yaml"
    data = yaml.safe_load(path.read_text()) or {}
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            data[k].update(v)
        else:
            data[k] = v
    data["last_checked"] = dt.date.today().isoformat()
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


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
