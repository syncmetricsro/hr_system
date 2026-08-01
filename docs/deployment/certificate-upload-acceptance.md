# Fictional certificate upload acceptance runbook

Use this check for both Jober and CorvinumEU after a certificate-related release
or before demonstrating the shared compliance workflow. It is a
**fictional-data staging/local check only**. Never substitute a real worker's
identity, birth, residence, financial, or medical document.

## What this check proves

- forklift, crane, and welding files can be uploaded through the normal UI;
- a front/back card and a single PDF both survive sanitation and private
  delivery;
- the form exposes only the three allowlisted occupational categories;
- the stored file remains behind the person/office sensitive-data permission;
- the audit and manager-only emergency purge paths remain available;
- changing the UI language does not change the stored category code or upload
  decision.

It does **not** prove that the application recognizes the words or visual
content of a document. The base product has no OCR, language detection,
translation, issuer verification, or automatic certificate classification.

## Tracked fictional fixture pack

A fresh repository checkout contains the curated pack at:

```text
tests/fixtures/manual_uploads/certificates/
```

Verify it from the repository root before use:

```bash
sha256sum --check tests/fixtures/manual_uploads/SHA256SUMS
```

The pack contains generated Testovia documents with synthetic people and
identifiers plus large `FICTIONAL TEST ...` / `NOT VALID` markings. It is
tracked strictly as a manual test fixture, never application seed data or a
deployment artifact. Generation originals, duplicate PNG/PDF forms, processed
previews and ZIPs remain gitignored; see the fixture `README.md` and
`PROVENANCE.md`. Never use a real document to complete this check.

## Positive UI checks

Perform these against a fictional person whose record is in the signed-in
user’s scope. Use a Manager/Admin when the later purge check is planned.

On Dokku staging, first confirm the active nginx configuration reports
`client_max_body_size 25m;` as described in
[`syncmetric-prime-staging.md`](syncmetric-prime-staging.md#required-upload-request-ceiling).
The application limit remains 10 MB per certificate file; 25 MB gives a
front-and-back request room to reach Django. A raw nginx 413 page is a proxy
configuration failure, not an application validation result.

1. Open the person's **Occupational certificates** panel and choose **Add
   certificate**.
2. Confirm the type picker contains only Forklift, Crane, and Welding.
3. Create a forklift record with:
   - type: Forklift;
   - issuer: `Testovia Safety Training Centre`;
   - certificate number: `DEMO-FL-001`;
   - issue date: `2026-07-01`;
   - expiry date: `2027-07-01`;
   - front: `allowed-forklift-front.png`;
   - back: `allowed-forklift-back.png`.
4. Save, then open both private file links. Each must return the correct side;
   neither URL is a public media-directory URL.
5. Create a crane record with `allowed-crane-certificate.pdf` as the **only**
   file. Confirm it saves and opens. A PDF plus a back image must be rejected.
6. Create a welding record with `allowed-welding-certificate.png`. Confirm the
   canonical Welding category and expiry are shown.
7. Open **Audit** and confirm the certificate creation events exist. The audit
   records file presence, not file bytes or a secret download URL.

Do not repeatedly add these records on shared staging. Reuse a designated
fictional person or archive/purge test records according to the cleanup section.

## Storage-boundary checks

The ordinary form must not offer Identity, Passport, Birth certificate,
Residence, Medical, Financial, Health, or unrestricted Other file categories.
That UI result is the normal acceptance check.

Server-side rejection of a crafted `HEALTH` or `OTHER` upload is covered by
`test_crafted_post_cannot_upload_disallowed_category` in
`tests/test_certificates.py`. Do not improvise a crafted request against shared
staging during a client demonstration.

### Optional internal mislabel probe

This probe documents a known limitation and is **not** a client-demo step:

1. On fictional staging, select Forklift but upload
   `prohibited-birth-certificate.pdf` or
   `prohibited-national-id-front-back.pdf`.
2. Current expected result: the upload is accepted because the server validates
   the selected category and safe file structure, not the pixels or words.
3. Record the result as `category allowlist enforced; semantic content not
   inspected`.
4. Immediately use the Manager-only **Permanently remove files** action with a
   reason such as `Fictional mislabel acceptance probe`.
5. Confirm the files no longer open and Audit contains the purge event while
   retaining the metadata/history row.

If this probe ever becomes rejected, stop and identify the deliberate feature
or regression that changed the behavior before updating this runbook. Content
classification would require a separate product/security decision and cannot
be assumed merely from a filename or OCR guess.

## Different-language certificate check

The file sanitizer is intentionally language-agnostic: it decodes/re-encodes
images or rebuilds safe PDF pages without reading text. A Slovak, Hungarian,
Ukrainian, or English occupational certificate therefore follows the same
upload path when an operator manually selects Forklift, Crane, or Welding.

Verified UI category labels:

| UI | Forklift | Crane | Welding |
|---|---|---|---|
| English | Forklift | Crane | Welding |
| Slovak | Vysokozdvižný vozík | Žeriav | Zváranie |
| Hungarian | Targonca | Daru | Hegesztés |
| Ukrainian | Навантажувач | Кран | Зварювання |

Jober exposes EN/SK/HU/UK. CorvinumEU exposes SK/HU. To rehearse multilingual
operation, switch the UI language, upload an unmistakably fictional
occupational scan written in a different language, and confirm the result is
unchanged. The language of the paper does not need to match the UI language.

Record the outcome precisely:

- **supported:** safe storage/delivery of a manually classified certificate in
  any language representable as pixels or PDF pages;
- **not supported:** detecting the document language, recognizing its type,
  reading its number/issuer/dates, translating it, or checking that typed
  metadata matches the scan.

## Cleanup and evidence

- Archive ordinary positive-test records if the history is useful.
- Permanently purge any deliberate wrong-document/mislabel probe immediately;
  only a Manager/Admin can do this and a reason is mandatory.
- Never run the destructive storage-policy management command as routine
  cleanup.
- Record client, environment, fictional person, selected category, file form
  (front/back or PDF), UI language, pass/fail result, cleanup, and relevant
  audit event in the rehearsal/deployment notes. Do not attach the document
  bytes to the journal.

The real-data gates and at-rest trust boundary remain in
[`../product/document-storage-boundary.md`](../product/document-storage-boundary.md)
and [`../product/certificate-upload-design.md`](../product/certificate-upload-design.md).
