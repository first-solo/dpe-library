# Catalog schema

One YAML file per document in `catalog/`. The filename stem must equal the
`id` field. The build fails if they drift apart.

## Fields

| Field | Required | Notes |
|---|---|---|
| `id` | yes | lowercase-hyphenated, **stable and revision-free**. `acs-private-airplane`, never `acs-6c`. Cross-references break if IDs move. |
| `title` | yes | Full document title as the FAA writes it. |
| `doc_number` | | `8900.1`, `FAA-S-ACS-6`, `8000.95`. |
| `type` | yes | `order` `notice` `ac` `acs` `pts` `handbook` `interpretation` `policy` `cfr` `other` |
| `status` | yes | `current` `superseded` `historical` `unknown` |
| `revision` | | Revision or change letter. |
| `effective_date` | | ISO date. |
| `source_url` | yes | Canonical landing page. |
| `pdf_url` | | Direct file link. Leave empty when the source serves HTML only. |
| `sha256` | | Hash of the last fetched copy, or of the tracked mirror copy. Written by `check_updates.py`, `fetch.py` and `mirror.py`. |
| `http` | | Stored ETag / Last-Modified / Content-Length. Written by `check_updates.py`. |
| `last_checked` | | ISO date. Written by `check_updates.py`. |
| `mirror` | | `true` to keep a tracked copy in `mirror/<id>.pdf`. For documents with no stable direct download, chiefly DRS exports. Set by `make mirror ID=<id> FILE=<path>`. The build fails if the copy no longer matches `sha256`. With no `pdf_url`, the README links to the copy. |
| `tags` | yes | Free-form subject keywords. |
| `applies_to` | | Certificates and ratings: `PVT-ASEL`, `CFI-A`, `ATP`, `ALL`. |
| `related` | | Other IDs. Validated; a dangling reference fails the build. |
| `supersedes` / `superseded_by` | | Other IDs. Also validated. |
| `interprets` | | 14 CFR citations a legal interpretation construes: `61.51(e)(1)(i)`, `1.1`, `141 Appendix B`. No `14 CFR` or `§` prefix. Validated for shape; drives the "By regulation" index. |
| `notes` | | **Public.** See the rule below. |
| `check` | | How the update checker handles this entry. |

Any string field containing `TODO` is reported under "Needs verification" in
the generated README rather than failing the build, so an entry can be stubbed
now and completed later.

## Legal interpretations

Chief Counsel letters have no document number, so they follow their own
conventions:

- **`id`** is `interp-<requester surname>-<year>`, with `-2`, `-3` for a
  second or third letter to the same person in the same year. This mirrors the
  FAA's own file naming (`Grannis-2_2016_Legal_Interpretation.pdf`). Year is
  the year on the FAA file, which is normally the letter's year.
- **`title`** is `Legal Interpretation to <requester as addressed>`, with the
  organisation in parentheses when the letter names one. Memoranda to Flight
  Standards say so in the title.
- **`effective_date`** is the date on the letter. Many date stamps are hard to
  read in the scans. When the stamp is partly illegible but other FAA letters
  cite the date, the date is recorded with a `# verify this` comment naming the
  citing letters. When nothing settles it, the field is `TODO` with a comment
  saying what the stamp shows.
- **`status`** starts as `unknown`. Interpretations get withdrawn or rescinded
  (`interp-carty-2022` rescinds two), and a letter should only be marked
  `current` once someone has checked it against the FAA database.
- **`interprets`** lists the provisions the letter actually construes, at the
  paragraph level the letter uses. It is the useful cross-reference for this
  type; `related` is kept for letters that cite each other.
- **`notes`** state the question the letter answers, not the answer. The
  holding is the letter's to state.
- **`check`** is `manual`. A letter does not change once issued; what changes
  is whether it is still in effect, which no automated check here can see.

## The notes rule

The split is not personal versus shareable. It is **citation versus
interpretation**.

`notes` in `catalog/` points at where an answer lives. "Retest and
discontinuance matrix is in Appendix A." "See Vol 5 Ch 2 Para 5-1234 for the
eligibility check." Navigation, verifiable against the source.

`private_notes` in `private/` says what something means. How you handle a grey
area, what your POI told you verbally, how you reconcile two documents that
disagree, what a given inspector expects. A note written by a sitting DPE reads
as authoritative to anyone who finds the repository, whether or not it was
meant that way, and it travels badly out of context.

While you build the catalog, notice which sentence you are writing. Pointer
goes public. Reading goes private.

## The private overlay

`private/<same-filename>.yaml` is merged on top of the public entry at build
time. Only include the keys you are adding or changing.

```yaml
# private/acs-private-airplane.yaml
private_notes: |
  Your reading of a grey area goes here.
tags_append: [watch-this]
status: unknown
```

- Dicts merge recursively, scalars and lists replace.
- A key ending in `_append` concatenates onto the public list of the same name,
  so you can add a tag without restating the public ones.
- `id` in an overlay is ignored.

Three things keep private content out of the repository, and they are
structural rather than a flag you have to remember:

1. `private/` and `local/` are in `.gitignore` from the first commit.
2. `build.py` writes tracked files (`README.md`, `site/index.json`) from a
   loader that never opens `private/`. Merged output only ever goes to
   `local/`, which is gitignored.
3. CI fails if `private/` becomes tracked or if `private_notes` appears in any
   tracked file.

Git history is forever. The overlay existing before the first commit is the
whole point.

## Update checking

```yaml
check:
  method: head
```

| Method | Behaviour |
|---|---|
| `head` | HEAD request, compares ETag / Last-Modified / Content-Length against stored values. Cheapest. Default choice for direct `faa.gov` PDFs. |
| `hash` | Downloads and compares sha256. Use when headers are unreliable. |
| `scrape` | Pulls a revision string off a landing page with `pattern` and compares to `revision`. |
| `list` | Counts unique `pattern` matches on an index page and compares to `check.seen_count`. Catches new legal interpretations appearing in a yearly list. |
| `manual` | Never checked automatically, but reported every run so it stays visible. |

`scrape` and `list` need a `pattern` with one capture group, and they default
to `source_url`. The others default to `pdf_url`.

DRS has no documented public API. Its single-page app is backed by JSON
endpoints visible in browser devtools, which would work but would break without
warning, so DRS-sourced entries are `manual` until you decide that trade is
worth making.

The exit code is 2 when anything changed, which is what the scheduled workflow
keys on when deciding to open a pull request.
