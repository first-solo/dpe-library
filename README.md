# DPE Reference Library

Curated index of FAA guidance used for practical tests. The PDFs are not
stored here; each entry links to the FAA source. Run `make fetch` to pull
local copies into `local/`.

**Nothing in this repository is authoritative.** Always confirm currency
against the FAA source before relying on a document.

Generated 2026-09-19 · 12 documents

## Contents

- [Orders](#orders)
- [Airman Certification Standards](#airman-certification-standards)
- [Practical Test Standards](#practical-test-standards)
- [Legal Interpretations](#legal-interpretations)
- [By certificate](#by-certificate)
- [By tag](#by-tag)

## Orders

- [Designee Management Policy](TODO)
  `8000.95` · Rev TODO · TODO
  `designee` `dpe` `oversight` `renewal` `managing-specialist`
  > Volume 2 covers designee selection and appointment; the oversight and
  > renewal expectations that actually affect you sit later in the order.
  See also: `order-8900-1-vol5-ch2`

- [FSIMS Order 8900.1 Vol 5 Ch 2 — Airman Certification, Practical Tests](https://drs.faa.gov/browse)
  `8900.1` · Rev TODO · TODO
  `practical-test` `examiner-conduct` `disapproval` `letter-of-discontinuance`
  > Catalogue individual volumes and chapters, not "the 8900." The order is
  > revised per-chapter and a whole-document entry will always be wrong.
  See also: `acs-private-airplane`, `order-8000-95`

## Airman Certification Standards

- [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf)
  `FAA-S-ACS-11` · Rev A · 2023-11-01
  `acs` `atp` `type-rating` `task-selection` `discontinuance` `retest` `eligibility`
  > Covers the type rating practical test as well as the ATP certificate, so it
  > applies to type rating rides conducted outside an ATP context.
  See also: `acs-commercial-airplane`, `acs-companion-guide-pilots`, `order-8900-1-vol5-ch2`

- [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf)
  `FAA-G-ACS-2` · Rev Changes 1 & 2 · 2024-12-26
  `acs` `companion-guide` `task-selection` `discontinuance` `retest` `eligibility`
  > Where the non-regulatory appendix material went when the ACS moved to
  > revision C. Look here first for test administration, task selection and
  > discontinuance guidance that older notes cite as an ACS appendix.
  > Dated by change rather than by revision letter: base November 2023,
  > Change 1 September 19 2024, Change 2 December 26 2024. effective_date
  > carries the Change 2 date, so it moves whenever a change is issued —
  > unlike the ACS entries, whose dates are fixed at the revision.
  See also: `acs-private-airplane`, `acs-commercial-airplane`, `acs-instrument-airplane`, `acs-cfi-airplane`, `acs-atp-airplane`

- [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf)
  `FAA-S-ACS-7` · Rev B · 2023-11-01
  `acs` `task-selection` `discontinuance` `retest` `eligibility`
  > Supersedes FAA-S-ACS-7A, Change 1. Non-regulatory appendix material moved
  > to FAA-G-ACS-2 (Companion Guide) at revision B — the 7B foreword carries
  > the same appendix-move language as 6C, in the same November 2023 wave.
  See also: `order-8900-1-vol5-ch2`

- [Commercial Pilot – Military Competence Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/mcn_acs.pdf)
  `FAA-S-ACS-12` · 2018-10-15
  `acs` `military-competence` `eligibility`
  > Standard for the military competence knowledge test route under 61.73.
  > Publication and effective dates differ here, unlike the rest of the ACS
  > set: the revision history gives August 2018, while the Availability page
  > says the material "will be effective October 15, 2018." The later date is
  > what effective_date carries.
  > Confirm against the document whether the applies_to list above is right —
  > it was inferred from the title, not read off the ACS.
  See also: `acs-commercial-airplane`, `acs-instrument-airplane`, `acs-companion-guide-pilots`

- [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf)
  `FAA-S-ACS-25` · 2023-11-01
  `acs` `cfi` `task-selection` `discontinuance` `retest` `eligibility`
  > Replaced FAA-S-8081-6 as the standard for the airplane flight instructor
  > practical test. The instrument instructor test is not covered here — that
  > is still a PTS, see pts-cfi-instrument-airplane.
  See also: `acs-private-airplane`, `acs-commercial-airplane`, `acs-companion-guide-pilots`, `order-8900-1-vol5-ch2`

- [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf)
  `FAA-S-ACS-8` · Rev C · 2023-11-01
  `acs` `instrument` `task-selection` `discontinuance` `retest` `eligibility`
  > Revision history on page ii lists FAA-S-ACS-8C as November 2023.
  See also: `acs-private-airplane`, `acs-commercial-airplane`, `acs-companion-guide-pilots`, `order-8900-1-vol5-ch2`

- [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
  `FAA-S-ACS-6` · Rev C · 2023-11-01
  `acs` `task-selection` `discontinuance` `retest` `eligibility`
  > Supersedes FAA-S-ACS-6B. Non-regulatory appendix material moved to
  > FAA-G-ACS-2 (Companion Guide) at revision C.
  See also: `order-8900-1-vol5-ch2`

## Practical Test Standards

- [Flight Instructor Instrument Practical Test Standards for Airplane Rating and Helicopter Rating](https://www.faa.gov/training_testing/testing/acs/cfi_instrument_pts_9.pdf)
  `FAA-S-8081-9` · Rev E · 2023-11-01
  `pts` `cfi` `instrument` `current-pts`
  > Still a PTS and still current — there is no instrument instructor ACS for
  > airplane, so a CFII ride runs against this rather than FAA-S-ACS-25.
  > Covers the helicopter rating in the same document.
  > The HEAD response carries no Last-Modified, so the update check falls back
  > to Content-Length alone.
  See also: `acs-cfi-airplane`, `acs-instrument-airplane`, `order-8900-1-vol5-ch2`

- [Flight Instructor – Airplane Practical Test Standards](TODO) *(superseded)*
  `FAA-S-8081-6` · Rev D · 2012-06-01
  `cfi` `legacy` `superseded`
  > Kept for applicants tested under the legacy standard and for tracing how
  > a task was worded before the ACS transition.
  > The document is off the FAA site, so the date above comes from the
  > FAA-S-ACS-25 revision history and foreword, both of which give the
  > superseded 8081-6D as June 2012. pdf_url stays unresolved for the same
  > reason — there is no upstream copy left to point at.
  See also: `acs-private-airplane`, `pts-cfi-instrument-airplane`

## Legal Interpretations

- [FAA Chief Counsel Legal Interpretations (index)](https://www.faa.gov/about/office_org/headquarters_offices/agc/practice_areas/regulations/interpretations)
  `legal-interpretation` `chief-counsel` `index`
  > Watcher entry, not a document. The list check flags when new
  > interpretations appear so individual ones can be catalogued.
  See also: `order-8900-1-vol5-ch2`

## By certificate

- **ALL** — [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf), [FAA Chief Counsel Legal Interpretations (index)](https://www.faa.gov/about/office_org/headquarters_offices/agc/practice_areas/regulations/interpretations), [Designee Management Policy](TODO), [FSIMS Order 8900.1 Vol 5 Ch 2 — Airman Certification, Practical Tests](https://drs.faa.gov/browse)
- **ATP** — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf)
- **CFI-A** — [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Flight Instructor – Airplane Practical Test Standards](TODO)
- **CFII-A** — [Flight Instructor Instrument Practical Test Standards for Airplane Rating and Helicopter Rating](https://www.faa.gov/training_testing/testing/acs/cfi_instrument_pts_9.pdf)
- **COM-AMEL** — [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Commercial Pilot – Military Competence Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/mcn_acs.pdf)
- **COM-AMES** — [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf)
- **COM-ASEL** — [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Commercial Pilot – Military Competence Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/mcn_acs.pdf)
- **COM-ASES** — [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf)
- **IR-A** — [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf)
- **PVT-AMEL** — [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- **PVT-AMES** — [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- **PVT-ASEL** — [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- **PVT-ASES** — [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)

## By tag

- `acs` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf), [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf), [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf), [Commercial Pilot – Military Competence Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/mcn_acs.pdf), [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- `atp` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf)
- `cfi` — [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Flight Instructor – Airplane Practical Test Standards](TODO), [Flight Instructor Instrument Practical Test Standards for Airplane Rating and Helicopter Rating](https://www.faa.gov/training_testing/testing/acs/cfi_instrument_pts_9.pdf)
- `chief-counsel` — [FAA Chief Counsel Legal Interpretations (index)](https://www.faa.gov/about/office_org/headquarters_offices/agc/practice_areas/regulations/interpretations)
- `companion-guide` — [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf)
- `current-pts` — [Flight Instructor Instrument Practical Test Standards for Airplane Rating and Helicopter Rating](https://www.faa.gov/training_testing/testing/acs/cfi_instrument_pts_9.pdf)
- `designee` — [Designee Management Policy](TODO)
- `disapproval` — [FSIMS Order 8900.1 Vol 5 Ch 2 — Airman Certification, Practical Tests](https://drs.faa.gov/browse)
- `discontinuance` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf), [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf), [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf), [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- `dpe` — [Designee Management Policy](TODO)
- `eligibility` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf), [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf), [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf), [Commercial Pilot – Military Competence Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/mcn_acs.pdf), [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- `examiner-conduct` — [FSIMS Order 8900.1 Vol 5 Ch 2 — Airman Certification, Practical Tests](https://drs.faa.gov/browse)
- `index` — [FAA Chief Counsel Legal Interpretations (index)](https://www.faa.gov/about/office_org/headquarters_offices/agc/practice_areas/regulations/interpretations)
- `instrument` — [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf), [Flight Instructor Instrument Practical Test Standards for Airplane Rating and Helicopter Rating](https://www.faa.gov/training_testing/testing/acs/cfi_instrument_pts_9.pdf)
- `legacy` — [Flight Instructor – Airplane Practical Test Standards](TODO)
- `legal-interpretation` — [FAA Chief Counsel Legal Interpretations (index)](https://www.faa.gov/about/office_org/headquarters_offices/agc/practice_areas/regulations/interpretations)
- `letter-of-discontinuance` — [FSIMS Order 8900.1 Vol 5 Ch 2 — Airman Certification, Practical Tests](https://drs.faa.gov/browse)
- `managing-specialist` — [Designee Management Policy](TODO)
- `military-competence` — [Commercial Pilot – Military Competence Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/mcn_acs.pdf)
- `oversight` — [Designee Management Policy](TODO)
- `practical-test` — [FSIMS Order 8900.1 Vol 5 Ch 2 — Airman Certification, Practical Tests](https://drs.faa.gov/browse)
- `pts` — [Flight Instructor Instrument Practical Test Standards for Airplane Rating and Helicopter Rating](https://www.faa.gov/training_testing/testing/acs/cfi_instrument_pts_9.pdf)
- `renewal` — [Designee Management Policy](TODO)
- `retest` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf), [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf), [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf), [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- `superseded` — [Flight Instructor – Airplane Practical Test Standards](TODO)
- `task-selection` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf), [Flight Instructor for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/cfi_airplane_acs_25.pdf), [Commercial Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/commercial_airplane_acs_7.pdf), [Airman Certification Standards Companion Guide for Pilots](https://www.faa.gov/training_testing/testing/acs/acs_companion_guide_pilots.pdf), [Instrument Rating – Airplane Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/instrument_rating_airplane_acs_8.pdf), [Private Pilot for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/private_airplane_acs_6.pdf)
- `type-rating` — [Airline Transport Pilot and Type Rating for Airplane Category Airman Certification Standards](https://www.faa.gov/training_testing/testing/acs/atp_airplane_acs_11.pdf)

## Needs verification

- order-8000-95.yaml: revision needs verification
- order-8000-95.yaml: effective_date needs verification
- order-8000-95.yaml: pdf_url needs verification
- order-8900-1-vol5-ch2.yaml: revision needs verification
- order-8900-1-vol5-ch2.yaml: effective_date needs verification
- pts-cfi-airplane.yaml: pdf_url needs verification
