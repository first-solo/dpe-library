# DPE Reference Library

A curated index of FAA guidance used by a Designated Pilot Examiner. Metadata
lives in git as one YAML file per document; everything else is generated. There
is no database and there should not be one — the catalog tops out in the low
hundreds of entries.

Read `SCHEMA.md` before editing anything in `catalog/`.

## The one invariant

**Private annotation content must never reach a tracked file.**

`private/<id>.yaml` overlays `catalog/<id>.yaml` at build time. The overlay is
where the owner records what a document *means* — readings of grey areas, what
a POI said verbally, how he reconciles conflicting guidance. A note written by a
sitting DPE reads as authoritative to anyone who finds this repo, so it stays
out of the published surface.

Three mechanisms enforce this, and all three must survive any refactor:

1. `private/` and `local/` are gitignored.
2. `dpelib.load_catalog(private=False)` physically does not open `private/`.
   Every tracked artifact (`README.md`, `site/`) is built from that call.
   Merged output goes only to `local/`.
3. `.github/workflows/verify.yml` fails if `private/` becomes tracked or if
   `private_notes` appears in a tracked file.

Do not add a flag, env var, or argument that lets private content be written to
a tracked path. The separation is structural on purpose — "remember to pass
`--public`" is not a safeguard. If a feature seems to need that, it's the wrong
feature.

The same split applies to instructions for you: project guidance goes in this
file, anything personal goes in `CLAUDE.local.md`, which is gitignored.

## Conventions that differ from what you'd assume

- **`id` is stable and revision-free.** `acs-private-airplane`, never
  `acs-6c`. Revision letters change and `related:` cross-references break when
  IDs move. Titles change too — the Private Pilot ACS was renamed at revision
  C — so never derive an ID from a title.
- **`id` must equal the filename stem.** The build warns when they drift.
- **`TODO` in a string field is tolerated, not an error.** It surfaces under
  "Needs verification" in the generated README. This is deliberate: entries get
  stubbed in bulk and verified in a second pass.
- **Catalog files may carry comments, and the tooling must keep them.**
  `# verify this` annotations are how the backfill's second pass finds its
  work. `check_updates.py` writes through `ruamel.yaml` in round-trip mode for
  exactly this reason, and `make test` fails if that regresses. Anything new
  that writes to `catalog/` has the same obligation — never `yaml.safe_dump`
  a catalog file.
- **`last_checked` must stay a quoted string.** Written bare it parses back
  as a `datetime.date`, and `json.dumps` rejects that when `build.py` writes
  `site/index.json`. This currently holds because `ruamel` quotes date-shaped
  strings on its own, not because anything enforces it — the round-trip test
  checks the line is present, not that the value survives a build.
- **Never resolve a `TODO` by guessing.** Revision letters, effective dates,
  and PDF URLs must come from the FAA source or from the owner. A plausible
  wrong date here is worse than a visible gap — this material governs real
  practical tests.
- **A dangling `related:` / `supersedes:` reference is fatal.** Keeps the
  cross-reference graph honest as the catalog grows.
- **PDFs that can be re-fetched are not committed.** `fetch.py` pulls anything
  with a working `pdf_url` into gitignored `local/pdfs/`. The exception is
  `mirror: true`, for documents with no stable download: DRS exports above all
  (8900.1 sections, 8000.95), plus superseded PTSs and pulled interpretations.
  On DRS the exported file, not the link, is the thing that is hard to get
  again. Add one with `make mirror ID=<id> FILE=<path>` (`scripts/mirror.py`),
  which copies it to `mirror/<id>.pdf` and records `mirror: true` and
  `sha256`. `build.py --check` fails if a copy drifts from its hash or if a
  file in `mirror/` has no entry. Don't mirror faa.gov PDFs that `fetch.py`
  can reach — the repo publishes curation, not copies of freely available
  files. Mirrored files are US government works, so there is no rights issue,
  but every replaced copy stays in history: mirror a new change when it is
  published, not on every re-export.
- **Commit catalog entries in batches**, not one commit per document.

## Commands

`make build` regenerates tracked output plus the private view in `local/`.
`make check` is the CI gate: validates and fails if tracked output is stale.
`make test` runs `tests/test_apply_updates.py`, which fails if the update
checker's writer starts reformatting catalog files, and `tests/test_mirror.py`.
All writes to `catalog/` go through `scripts/catalog_writer.py`. `make fetch` downloads
PDFs. `make updates` checks upstream; `make updates-write` also records hashes
and `last_checked`. CI runs `check` and `test` on every push.

Everything runs in Docker so nothing installs on the owner's machine — he
prefers isolated environments and that preference should be respected when
proposing tooling. The dependencies are PyYAML for reading and `ruamel.yaml`
for the one writer that touches catalog files; scripts also run directly with
`PYTHONPATH=scripts`.

## Domain pitfalls

- **Order 8900.1 is not a document.** It's revised per section, and sections
  of one chapter sit on different CHG numbers. Catalog sections
  (`order-8900-1-vol5-ch2-sec7`), each with its own `revision: CHG nnn`. A
  chapter entry (`order-8900-1-vol5-ch2`) is an index with no revision of its
  own. Never catalog the order as a whole.
- **DRS has no documented public API.** Its SPA is backed by JSON endpoints
  visible in devtools, which would work and would break without warning.
  DRS-sourced entries are `check: {method: manual}` until the owner decides
  that trade is worth making. Don't wire it up unprompted.
- **ACS appendix material moved.** At FAA-S-ACS-6C much of the non-regulatory
  appendix content moved to FAA-G-ACS-2, the Companion Guide. Notes referencing
  ACS appendices may be stale for any document at revision C or later.
- **Legal interpretations don't have document numbers.** They're identified by
  requester and date, and the useful cross-reference is the regulation they
  interpret, not other documents. `interprets:` carries that; see the
  conventions in `SCHEMA.md`. Public `notes` on a letter state the question it
  answers, never a summary of the holding.

## Current state

Scaffold complete and pushed. 65 catalog entries: the original six (three of
them stubs) plus 59 legal interpretations, which brought in the `interprets:`
field and a "By regulation" index in the README.
`acs-private-airplane` and `acs-commercial-airplane` are real: verified URLs,
`check: head`, baselines recorded. `interp-agc-index` is a `list` watcher
rather than a document. The update loop has been proven end to end, including
a live `--write` that moved only the lines it was supposed to.

The writer no longer destroys comments or formatting — that was the first item
on this list and it is done. `make test` guards it. Both workflows run on
Node 24 actions, and the scheduled `check-updates` run has been exercised by
hand; it had never actually worked before, because `tee` wrote into a
gitignored `local/` that does not exist on a fresh runner.

## Open work, roughly in order

1. **Backfill the catalog.** Stub broadly first — title, doc number, type,
   tags, `TODO` elsewhere — then verify in a second pass. The schema has only
   met six documents; expect it to need changes. Annotating stubs with
   `# verify this` is safe now that the writer preserves comments.
2. **Finish the legal interpretations.** 59 Chief Counsel letters are
   catalogued with `interprets:` citations, all `status: unknown` with
   `pdf_url: TODO`. Remaining: record the direct faa.gov PDF links, resolve the
   dates marked `TODO` or `# verify this`, and mark each letter `current` only
   after checking it against the FAA database. Legal interpretations also
   respond to rule changes after the letter (BasicMed in 2017, and the part 61
   amendments since), so "not withdrawn" is not the same as "still accurate".
3. **Local HTML view (private).** `build.py` emits `local/index.html`
   alongside the existing markdown: a self-contained page opened by
   double-clicking, no server. Links to FAA sources and to local copies in
   `local/pdfs/`. Client-side search over the existing index using MiniSearch
   or Lunr. Built from the merged catalog including the private overlay
   (`load_catalog(private=True)`), so it lands only in gitignored `local/`.
   No publishing decision involved — this is the day-to-day working surface.
4. **Public HTML view (GitHub Pages).** Same generator, built public-only,
   linking to FAA sources rather than local files. Two constraints to decide
   before writing it.

   Pages deploying from a branch can only serve the repo root or `/docs`, not
   an arbitrary `site/` directory. So either rename `site/` to `docs/`, which
   touches `dpelib.py`, the Makefile and both workflows, or deploy via Actions
   with `upload-pages-artifact`, which can publish any directory. Prefer the
   Actions route — the rename is wide and we already run workflows.

   Enabling Pages also makes the content publicly readable regardless of repo
   visibility. This item is blocked on the decision to publish, not on the
   code; the repo stays private while the notes convention settles.
5. **Full-text search.** `poppler-utils` is already in the image for
   `pdftotext`. Extract into per-document JSON loaded on demand — do not inline
   full text into the main index, it will not stay small.

Smaller, not urgent:

- The `check-updates` workflow reports through a single standing issue,
  "Upstream check needs attention": commented on every flagged run (rc=2),
  closed on the first clean one. The pull request step runs unconditionally
  and relies on `create-pull-request` no-oping when nothing changed, which
  holds only because the tracked README carries no build date. Never put a
  date or anything else time-varying back into tracked output; it makes
  `make check` fail on every later day and makes every run open a PR.
- A `list` or `scrape` check that matches nothing is `PATTERN MISSED`, not a
  count of zero. `interp-agc-index` currently does this — its pattern has
  never matched the real page — and needs fixing against the live page.
- The `rc=2` path of that workflow is still unexercised — it needs a real FAA
  document to move. Expect the first genuine drift to be the test.

## Working style

The owner is an experienced pilot and DPE, and a capable developer. Be direct,
skip the preamble, and don't explain FAA concepts to him. Do flag regulatory
detail you're unsure of rather than asserting it — accuracy about FAA material
matters more here than in most projects, and a confident wrong answer about
guidance is a real cost.
