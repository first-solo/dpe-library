#!/usr/bin/env python3
"""Confirm check_updates.apply_updates() only ever touches its own fields.

The checker writes four things and nothing else: `http`, `sha256`,
`check.seen_count`, and `last_checked`. Everything else in a catalog file —
comments, block scalars, empty values, key order, quoting — must come out the
far side byte-identical, because catalog entries carry `# verify this`
annotations during backfill and losing one silently is the worst failure this
repo has.

Run it directly (no pytest):

    PYTHONPATH=scripts python tests/test_apply_updates.py

or `make test`. Exit status is 0 on pass, 1 on failure.
"""

from __future__ import annotations

import difflib
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import check_updates as C
import dpelib as L

FIXTURE = pathlib.Path(__file__).resolve().parent / "fixtures" / "fixture-roundtrip.yaml"

# The complete write surface. A changed line naming any other key is a bug,
# and a changed line naming no key at all (a comment, a block scalar body) is
# a worse one.
WRITABLE = {"sha256", "last_checked", "etag", "last_modified",
            "content_length", "seen_count"}

# Applied in a single call. The real checker never emits sha256 and http
# together — one entry uses `hash`, another uses `head` — but exercising the
# whole surface at once is strictly harder and catches cross-talk between the
# merge paths.
UPDATES = {
    "sha256": "b" * 64,
    "http": {
        "etag": '"9f8e7d6c"',
        "last_modified": "Mon, 01 Sep 2025 00:00:00 GMT",
        "content_length": "999999",
    },
    "check": {"seen_count": 14},
}

KEY_RE = re.compile(r"^\s*([A-Za-z0-9_]+):")

failures: list[str] = []


def check(condition: bool, label: str, detail: str = "") -> None:
    if condition:
        print(f"  ok    {label}")
    else:
        print(f"  FAIL  {label}")
        if detail:
            print("\n".join(f"          {line}" for line in detail.splitlines()))
        failures.append(label)


def comments(text: str) -> list[str]:
    """Every comment in the file, full-line and end-of-line alike.

    Crude on purpose: a '#' inside a quoted scalar would be a false positive,
    and the fixture deliberately has none.
    """
    out = []
    for line in text.splitlines():
        if "#" in line:
            out.append(line[line.index("#"):].strip())
    return out


def top_level_keys(text: str) -> list[str]:
    return [m.group(1) for line in text.splitlines()
            if (m := re.match(r"^([A-Za-z0-9_]+):", line))]


def block_scalar_body(text: str) -> list[str]:
    """The literal lines under `notes: |`, verbatim, indentation included."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^notes:\s*\|", line):
            body = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt.startswith("  "):
                    break
                body.append(nxt)
            return [b for b in body if b.strip()]
    return []


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="dpe-roundtrip-"))
    try:
        # apply_updates() resolves its path through L.CATALOG, so pointing that
        # at a temp copy keeps the real catalog out of the test entirely.
        shutil.copy(FIXTURE, tmp / "fixture-roundtrip.yaml")
        L.CATALOG = tmp

        before = (tmp / "fixture-roundtrip.yaml").read_text()
        C.apply_updates("fixture-roundtrip", UPDATES)
        after = (tmp / "fixture-roundtrip.yaml").read_text()

        print("\n--- diff after apply_updates() "
              + "-" * 40)
        diff = list(difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            fromfile="before", tofile="after", lineterm="", n=1))
        print("\n".join(diff) if diff else "(no change)")
        print("-" * 70 + "\n")

        # 1. Comments survive, every one of them.
        lost = [c for c in comments(before) if c not in comments(after)]
        check(not lost, "all comments preserved",
              "lost:\n" + "\n".join(f"  {c}" for c in lost) if lost else "")

        # 2. The block scalar stays a block scalar, body byte-identical.
        check("notes: |" in after, "notes: stays a literal block scalar",
              "" if "notes: |" in after
              else "notes: is now " + next(
                  (l for l in after.splitlines() if l.startswith("notes:")), "absent"))
        check(block_scalar_body(before) == block_scalar_body(after),
              "notes: body unchanged",
              "before:\n" + "\n".join(block_scalar_body(before))
              + "\nafter:\n" + "\n".join(block_scalar_body(after)))

        # 3. An empty value stays empty rather than becoming an explicit null.
        check(re.search(r"^pdf_url:\s*$", after, re.M) is not None,
              "empty pdf_url: stays empty",
              "found: " + next(
                  (l for l in after.splitlines() if l.startswith("pdf_url")), "absent"))

        # 4. Both list styles the catalog uses survive as written.
        check("applies_to: [PVT-ASEL, PVT-AMEL]" in after,
              "flow-style list stays inline",
              "found: " + next(
                  (l for l in after.splitlines() if l.startswith("applies_to")), "absent"))
        check(re.search(r"^- acs$", after, re.M) is not None,
              "block-style list keeps its indentation")

        # 5. A quoted regex keeps its quotes. Unquoted, a pattern beginning
        #    with a YAML indicator character would not survive the next read.
        check("pattern: '([0-9]{4}-[0-9]+)'" in after, "quoted pattern keeps quotes",
              "found: " + next(
                  (l for l in after.splitlines() if "pattern:" in l), "absent"))

        # 6. Long values stay on one line. A default-width dumper folds them.
        check(re.search(r"^source_url: \S+$", after, re.M) is not None,
              "long source_url not wrapped",
              "found:\n" + "\n".join(
                  l for l in after.splitlines() if "faa.gov" in l or "interpretations" in l))

        # 7. Key order is untouched.
        check(top_level_keys(before) == top_level_keys(after),
              "top-level key order unchanged",
              f"before: {top_level_keys(before)}\nafter:  {top_level_keys(after)}")

        # 8. Only writable fields appear in the diff.
        offenders = []
        for line in diff:
            if line.startswith(("---", "+++", "@@")) or not line[:1] in "+-":
                continue
            body = line[1:]
            if not body.strip():
                continue
            m = KEY_RE.match(body)
            if m is None or m.group(1) not in WRITABLE:
                offenders.append(line)
        check(not offenders, "diff touches only the write surface",
              "unexpected lines:\n" + "\n".join(offenders) if offenders else "")

        # 9. The updates actually landed — a writer that changes nothing would
        #    otherwise sail through every check above.
        check("b" * 64 in after, "sha256 written")
        check('"9f8e7d6c"' in after, "http.etag written")
        check("999999" in after, "http.content_length written")
        check("seen_count: 14" in after, "check.seen_count written")
        check(re.search(r"^last_checked:", after, re.M) is not None,
              "last_checked written")
        check("method: list" in after, "check.method left alone")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if failures:
        print(f"\n{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
