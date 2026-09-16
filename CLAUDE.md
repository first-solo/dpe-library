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
- **Never resolve a `TODO` by guessing.** Revision letters, effective dates,
  and PDF URLs must come from the FAA source or from the owner. A plausible
  wrong date here is worse than a visible gap — this material governs real
  practical tests.
- **A dangling `related:` / `supersedes:` reference is fatal.** Keeps the
  cross-reference graph honest as the catalog grows.
- **PDFs are not committed.** `fetch.py` pulls them into gitignored
  `local/pdfs/`. The exception is `mirror: true`, for documents genuinely hard
  to find upstream (superseded PTSs, pulled interpretations). Don't change this
  default — the repo publishes curation, not copies of freely available files.
- **Commit catalog entries in batches**, not one commit per document.

## Commands

`make build` regenerates tracked output plus the private view in `local/`.
`make check` is the CI gate: validates and fails if tracked output is stale.
`make fetch` downloads PDFs. `make updates` checks upstream; `make
updates-write` also records hashes and `last_checked`.

Everything runs in Docker so nothing installs on the owner's machine — he
prefers isolated environments and that preference should be respected when
proposing tooling. PyYAML is the only dependency; scripts also run directly
with `PYTHONPATH=scripts`.

## Domain pitfalls

- **Order 8900.1 is not a document.** It's revised per volume and chapter in
  DRS. Catalog specific chapters (`order-8900-1-vol5-ch2`), never the order as
  a whole.
- **DRS has no documented public API.** Its SPA is backed by JSON endpoints
  visible in devtools, which would work and would break without warning.
  DRS-sourced entries are `check: {method: manual}` until the owner decides
  that trade is worth making. Don't wire it up unprompted.
- **ACS appendix material moved.** At FAA-S-ACS-6C much of the non-regulatory
  appendix content moved to FAA-G-ACS-2, the Companion Guide. Notes referencing
  ACS appendices may be stale for any document at revision C or later.
- **Legal interpretations don't have document numbers.** They're identified by
  requester and date, and the useful cross-reference is the regulation they
  interpret, not other documents. The schema does not yet handle this well.

## Current state

Scaffold complete and pushed. Five catalog entries exist, four of them stubs.
`acs-private-airplane` is the one real entry: verified URL, `check: head`,
baseline recorded. The update loop has been proven end to end.

## Open work, roughly in order

1. **Backfill the catalog.** Stub broadly first — title, doc number, type,
   tags, `TODO` elsewhere — then verify in a second pass. The schema has only
   met five documents; expect it to need changes.
2. **An `interprets:` field** for legal interpretations, holding CFR
   references (`interprets: [61.129, 61.195]`). Proposed, not agreed. Raise it
   when the first real interpretations get catalogued rather than building it
   speculatively.
3. **HTML output.** `build.py` should emit `local/index.html` (private, links
   to `local/pdfs/`) and `site/index.html` (public, links to FAA). Client-side
   search over the existing `index.json` using MiniSearch or Lunr from a CDN,
   no backend. This was deferred, not rejected.
4. **Full-text search.** `poppler-utils` is already in the image for
   `pdftotext`. Extract into per-document JSON loaded on demand — do not inline
   full text into the main index, it will not stay small.
5. **GitHub Pages** once the public surface is worth publishing. The repo is
   private for now; that's intentional while the notes convention settles.

## Working style

The owner is an experienced pilot and DPE, and a capable developer. Be direct,
skip the preamble, and don't explain FAA concepts to him. Do flag regulatory
detail you're unsure of rather than asserting it — accuracy about FAA material
matters more here than in most projects, and a confident wrong answer about
guidance is a real cost.
