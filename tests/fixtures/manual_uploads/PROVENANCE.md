# Fixture provenance

Created on 2026-08-01 for this repository's fictional local/staging acceptance
checks.

- The five avatar portraits were generated independently with Codex's built-in
  image generation. Each prompt required an entirely synthetic adult who does
  not resemble a real person; no input photograph or real-person reference was
  supplied. The JPEG/WebP upload variants and harmless test EXIF were produced
  locally using the project's already-approved Pillow dependency.
- The document images were generated independently as product mockups for the
  invented country Testovia. Every prompt prohibited real country names,
  government seals, real issuers, real identifiers, real photographs,
  signatures, barcodes, QR codes, and authentic security features. Each asset
  carries prominent `FICTIONAL TEST DOCUMENT` or `FICTIONAL TEST CERTIFICATE`
  and `NOT VALID` markings.
- PDF forms were derived locally from those fictional image fixtures using the
  project's existing PDF/image toolchain. No external document template or
  downloaded media was used.

Fictional labels include `OLHA TESTOVA`, `MILA TESTOVA`, `MIRA NOVAKOVA`,
`ANH NGUYEN`, `REPUBLIC OF TESTOVIA`, and the `DEMO-*`/`TEST-*` identifiers.
They are test data, not assertions about any real person or organization.

The committed binary set is deliberately curated. Generation originals and
duplicate processed/packaged forms are excluded to avoid permanent Git bloat.
`SHA256SUMS` identifies every committed binary exactly.
