# Paper archive register — module design

> **Designed, not built.** Nothing here is in the product. It is written to be
> priced, argued with, and approved or dropped before any code exists — the
> same treatment as [`secure-document-vault-design.md`](secure-document-vault-design.md).
>
> Prepared 2026-08-05, from an owner proposal. The boundary it sits inside:
> [`document-storage-boundary.md`](document-storage-boundary.md) (adopted
> 2026-07-31). Open client questions: **C-Q7**, **C-Q23**.

## The proposal

The office keeps physical papers — medical certificates, permits, licences,
signed contracts. The product should track *that they exist and when they
expire*, without ever holding a scan. For each paper the system mints a unique
identifier and prints a small label carrying a QR code, which the office sticks
on the archive sleeve so the paper can be found again and tied back to its
record.

**This is the right idea, and the boundary document already asked for it.**
`document-storage-boundary.md` requires every future document type to be
expressed as `METADATA_ONLY`, `FILE_ALLOWED`, or `PROHIBITED`, and closes with
*"a broader metadata-requirement catalogue remains separate future work."* This
register is that catalogue, plus a locator for the physical archive.

## Scope: work papers only

Confirmed with the owner on 2026-08-05. In scope:

- medical / fitness certificates
- work and residence permits
- occupational licences (forklift, crane, welding — which also hold files)
- signed contracts

Out of scope: identity cards, passports, birth and civil-status certificates.
Not because tracking them is unthinkable, but because a register that records
*"we hold this person's birth certificate"* is the product documenting that the
office retains prohibited-class papers. That needs a lawful basis, a retention
period, and in all likelihood a DPIA — decided before any code, not discovered
after it ships.

## Why this is worth building

### 1 · The QR token replaces the document number

This is the strongest argument and the least obvious one.

The boundary forbids copying full identifiers into the product: no ID numbers,
no certificate numbers for the prohibited classes. But an office genuinely
needs to say *which piece of paper* it means. Today the only way to do that is
to type the number into a note — the exact thing the boundary prohibits, done
under pressure because there is no alternative.

An opaque token gives them one. `A7K2-QX91` is the office's own reference for a
sheet in a folder; it is meaningless outside the system, it identifies no
person, and it can be printed, spoken over the phone, and written in a ledger
without disclosing anything. **The register does not merely comply with the
boundary — it removes the pressure to break it.**

### 2 · Expiry chasing stops being one field on one screen

The medical already works this way as of 2026-08-05: a date, an annual expiry,
a badge, an alert at 30 days, and a refusal to activate on a lapsed one. That
pattern is right and it is currently hard-coded for exactly one document type.
The register generalises it — each paper type carries its own validity rule, so
a permit that expires in March is chased the same way.

### 3 · It answers "what do we actually hold on this person?"

Under GDPR Article 30 the employer must be able to describe its processing. An
office that keeps paper in a cabinet and nothing in software cannot answer that
question except by opening the cabinet. A register answers it, per person, in
one screen — and makes an erasure request tractable, because you can tell what
has to be pulled and shredded.

## What it is not

- **Not the Secure Document Vault.** The vault stores files; this stores none.
  If the client hears "document management" the framing has failed.
- **Not storage of any kind.** No scans, no photographs, no PDFs of the paper.
- **Not verification.** The system never sees the document, so it cannot say
  the paper is genuine, current, or about the person named. A record is a
  human's claim, timestamped and attributed — exactly like a checklist tick.
- **Not a replacement for the accountant handoff rules**
  ([`accountant-data-handoff.md`](accountant-data-handoff.md)). Knowing a paper
  exists does not make it lawful to forward it.

## The shape

### Data

A `PaperType` catalogue (client-configurable, seeded): name, whether it
expires, default validity in months, whether it is required for activation,
and its boundary class. A `PaperRecord` per person per paper: type, the
office's own token, the dates the office read off it (issued, expires),
recorded-by and recorded-at, and where it is filed as free text the office
controls ("cabinet 2, folder K"). **No document numbers, no issuer identifiers,
no notes field that invites transcription.**

The validity rule lives on the type, not in a global constant — which also
retires the `MEDICAL_VALIDITY_MONTHS` single-number problem raised in C-Q7.

### The token and the label

- Random, not sequential: `features/feedback/models.py::_new_token` is the
  precedent already in the repo. A sequential number leaks how many workers the
  office has and invites guessing at the resolve URL.
- Rendered by `core/ui/qr.py` — `qr_svg` for the screen, `qr_pdf` for the
  printable sheet. **segno and fpdf2 are already pinned**, so there is no new
  dependency and no ADR under AGENTS.md §3.1.
- The QR encodes a URL ending in the token and nothing else. Someone who
  photographs a label in the archive learns nothing; the URL resolves only for
  an authenticated user, through the office scoping every other queryset uses
  (`core/offices/scoping.py`).
- Printed as a sheet of small labels, not one A4 per paper — the feedback flyer
  is a poster, this is stationery, and the office will print in batches.

### The label goes on the sleeve, never on the document

**This is the one part of the proposal to change.** Adhesive on a passport,
identity card, or an original certificate risks defacing an official document,
and an altered identity document is invalid in several jurisdictions — the
worker would carry the consequence, not the office. Label the sleeve, folder,
or envelope that holds the paper.

For papers the office owns outright (its own contract copy) a label on the sheet
is fine, but one rule is easier to train than two.

## Risks worth stating before it is approved

**The register lies if the office skips a label.** A physical step is only as
good as the habit, and a half-labelled archive is worse than none because it
looks complete. Mitigations: print the label at the moment the paper is
recorded, in the same action; and show unlabelled papers as *not registered*
rather than *missing*, so a partial rollout reads as partial rather than as an
alarm.

**It creates a retention duty.** A list of which papers exist for which person
is personal data in its own right, and for a medical it is health-adjacent.
C-Q13 and C-Q16 (retention periods) move from open to blocking.

**It invites scope creep toward the vault.** The first request after "we can
see what we hold" is "can we attach a scan". The answer stays no, and the
answer is easier to hold if the register never grows a file field even for
allowed types — those already live in `Certificate`.

## Reuse

Nothing here needs new infrastructure:

| Need | Already exists |
|---|---|
| Expiry severity, badges, alerts | `features/compliance` — `_severity`, `certificate_badges`, `compliance_alerts` |
| Month arithmetic | `core/dates.py::add_months` |
| QR + printable PDF | `core/ui/qr.py`; segno + fpdf2 pinned |
| Opaque tokens | `features/feedback/models.py::_new_token` |
| Audit, office scoping, RBAC | `core/audit`, `core/offices/scoping.py`, `core/accounts/permissions.py` |

Size is comparable to the existing certificates feature: a model and catalogue,
a person panel, a label PDF, a token resolve view, and the expiry rules wired
into the alerts that already exist.

## What to ask the client (C-Q23)

1. Which papers does the office actually keep, and which of them expire?
   (This is also the answer to C-Q7.)
2. Would they run a labelling step at all — every paper, every time?
3. Where do the papers physically live, and who may look at the register?
4. How long do they keep each type after a worker leaves?

If the answer to (2) is anything short of "yes, reliably", build the catalogue
and the expiry chasing and drop the labels. Two thirds of the value is in
knowing what exists and when it lapses; the QR only pays for itself if the
archive is actually indexed.
