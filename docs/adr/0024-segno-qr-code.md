# ADR 0024: QR codes for 2FA enrollment via segno

Status: **Accepted — owner approved 2026-07-11**

## Context

2FA setup (stdlib TOTP, Stage B4b) shows only the base32 secret and the
`otpauth://` URI; ADR 0023 recorded "no QR image — that would need a vendored
lib + ADR" as a deferral. Demo testing on the CorvinumEU client (where 2FA is
mandatory for managers) confirmed manual entry is too hostile: **QR codes are
required** (owner, 2026-07-11).

## Decision

Generate the QR **server-side as inline SVG** with **`segno==1.6.6`**
(published 2025-03-12 — cooldown satisfied by over a year; BSD-3 license;
maintained by Lars Heuer/heuer; **zero transitive dependencies**, pure
Python). The SVG embeds directly in the setup page: no external requests, no
JavaScript, the secret never leaves the existing page that already displays
it in text form.

Alternatives rejected:
- **Hand-rolled stdlib QR** — Reed–Solomon ECC + mask evaluation is ~300
  lines of subtle custom code on a security-relevant path; a vetted tiny
  library is less total risk.
- **Vendored JS QR renderer** — would be our first vendored JS beyond
  htmx/Alpine (§3.2 manifest upkeep) and moves rendering client-side for no
  benefit.

## Consequences

- `segno` is hash-pinned into `runtime.lock` + `test.lock` (wheel-only,
  resolved in the digest-pinned build container).
- QR renders dark-on-light on a white backing plate so scanners work against
  dark client themes.
- The manual secret + URI remain on the page as the fallback path.
