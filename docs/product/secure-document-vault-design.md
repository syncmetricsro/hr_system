# Secure Document Vault — module design

> **Designed, not built.** A deferred, separately scoped and separately priced
> module. Nothing here is in the product, and nothing here changes the base
> platform's document boundary, which is already decided and enforced.
>
> Prepared 2026-08-03. Client-facing version:
> [`secure-document-vault-proposal.md`](secure-document-vault-proposal.md).
> The boundary this sits behind:
> [`document-storage-boundary.md`](document-storage-boundary.md) (adopted
> 2026-07-31). Open client question: **C-Q18**.

## What this is

A controlled custodian for exactly the document classes the base product
**refuses to hold** — identity papers, civil-status documents, medical papers —
for a client with a demonstrated lawful need to retain them.

## What it is not

- Not a general-purpose file store or an "other HR attachments" feature.
- Not a way to relax the base boundary. The prohibited classes stay prohibited
  *in the base product* whether or not a vault exists.
- Not OCR, language detection, or automatic verification of what a scan depicts.
  The base product explicitly disclaims this and the vault adds none of it — a
  scan is stored as pixels and classified by a human.
- Not a replacement for the accountant handoff rules in
  [`accountant-data-handoff.md`](accountant-data-handoff.md). A vault does not
  make it lawful to forward a document that should not be forwarded.

## Why it is a separate module rather than a base feature

The base platform's position is that it does not hold this material. That is a
security property, not a gap: it caps breach impact, keeps the legal surface
small, and is what lets the product ship without a DPIA on identity documents.
Folding the vault into the base would surrender that property for every client
including the ones who never asked for it.

## What the base platform already provides

Cited rather than restated, because these are **not** part of what a vault would
add and listing them as features would imply otherwise:

| | Where |
|---|---|
| Server-side RBAC on every gated action, office scoping on every queryset | `core/accounts/permissions.py`, `core/offices/scoping.py` |
| Object-level authorisation before a file is served | `core/media_views.py::certificate_document` — `assert_person_in_scope` **and** `can_view_sensitive` |
| Append-only audit of mutations | `core/audit` |
| Secrets from a runtime manager, never Git or build layers | Doppler; `AGENTS.md` §3 |
| Hash-locked dependencies, digest-pinned images, no CDN assets | `AGENTS.md` §3.1 |
| Encrypted off-site backups with a restore drill that compares per-table row counts | `scripts/backup_restore_drill.sh`, `scripts/offsite_backup.sh` |
| 2FA required for manager roles | `TWO_FACTOR_AUTH_ENABLED` + `TWO_FACTOR_REQUIRED_ROLES` (CorvinumEU staging/production; localhost demo exempt) |
| A closed real-data gate | `AGENTS.md` |

## The three gaps the vault actually closes

Verified against the code on 2026-08-03. These are the honest differentiators.

**1 · Reads are authorised but not recorded.** `core/media_views.py` contains no
`record_event` call. Access to a certificate file is correctly *refused* to the
wrong person, but when the right person opens it nothing is written down. For an
identity document, "who looked at this, and when" is usually the control an
auditor asks for first.

**2 · Files are not encrypted with an application-managed key.** They are plain
`FileField`s on the client's Dokku media volume. `document-storage-boundary.md`
§"Current at-rest trust boundary" already states this, and
`production-readiness.md` tracks it as an open item blocking real scans: an
active host root can read the mounted volume regardless of disk encryption.

**3 · There is no re-authentication step.** Nothing in the codebase asks a user
to prove who they are again before a sensitive view or export. Session security
is the only barrier between a logged-in browser and every file that user may
see.

## Architecture

Only the vault-specific layers are specified. Everything in the table above is
inherited.

```text
Base platform (unchanged)
  person record ── status + opaque vault reference ──┐
  blacklist HMAC fingerprints (stay here)            │
                                                     ▼
                                          Vault access gateway
                                            · authorises every read
                                              independently of the base
                                            · re-auth for view/export
                                            · read + write audit
                                                     │
                    ┌────────────────────────────────┼───────────────────┐
                    ▼                                ▼                   ▼
        encrypted object store            encrypted identifier      retention
        (files, per-object keys)          values + fingerprints       engine
                    │                                │                   │
                    └──────── key management service ┘        delete / anonymise
                                                              archive / review
```

**Access gateway.** Every read is authorised by the vault itself, not trusted
because the base platform already allowed it. Two independent decisions, so a
flaw in one does not open the other. This is the single most important property
and the reason the vault is not simply "an encrypted folder".

**Object store.** Files identified by opaque random keys, never by name or
identifier. No public URLs, no static serving, no long-lived signed links.
Malware scanning and quarantine before a file becomes retrievable; strict type
and size validation; secure deletion including temporary and preview artefacts.

**Key management.** Per-object keys held by a key service the application does
not own, so a database compromise is not a file compromise, and an application
host root is not automatically a document reader. **This is what actually closes
gap 2**; storing ciphertext next to its key would not.

**Identifier storage.** `PersonIdentifier` lives **here, not in the base**:

| Field | Purpose |
|---|---|
| encrypted value | the exact identifier, decryptable only by an authorised workflow |
| fingerprint | keyed hash for duplicate detection without decryption |
| type, country | what kind of document, issued where |
| issue / expiry date, status | validity, without reading the value |

The base platform continues to store **no raw identifier at all**. The existing
blacklist path is unaffected: `MatchFingerprint` holds `identifier_type`, `hmac`
and `key_version` and never a value, and it stays in the base so re-entry
matching keeps working with or without a vault.

**Retention engine.** Per-record-type policy with four outcomes — delete,
anonymise, archive, or queue for human review — and scheduled execution. The
base has nothing comparable: `jober-data-retention-proposal.md` found only two of
ten personal-data stores have any purge path, and `run_retention` is not
scheduled anywhere. Ambiguous cases must go to a queue rather than being decided
by a cron job.

## The integration seam

The base retains **status plus an opaque vault reference, and never a copy**.
This is `document-storage-boundary.md`'s own rule, so it is a constraint on the
design rather than a choice within it.

| Direction | Crosses the seam |
|---|---|
| base → vault | a reference, and the acting user's identity for the vault's own authorisation |
| vault → base | status, validity dates, verification actor/time — the metadata the base is already allowed to hold |
| never crosses | the file, the decrypted identifier, any document contents |

A compliance panel can therefore say "verified, valid to 2027-07-01" without the
base platform ever holding the underlying document.

## Phasing

So it can be quoted in stages rather than as one number.

1. **Discovery and legal** — per-document necessity assessment, DPIA, threat
   model, key-ownership decision. Produces a go/no-go, and is worth doing even
   if the build never follows.
2. **Store and gateway** — encrypted object store, key service, access gateway
   with independent authorisation, read/write audit, upload sanitation.
3. **Base integration** — the reference field, status round-trip, compliance
   panel surfacing.
4. **Identifiers** — `PersonIdentifier` and fingerprint matching.
5. **Retention engine** — policies, scheduling, review queue.
6. **Operations** — encrypted backups with restore drills for the vault
   specifically, monitoring, incident runbook, access reviews.

Phases 1–2 are the bulk of the risk. Phase 4 can be dropped entirely if the
client only needs documents.

## What it costs to run, not just to build

Worth stating early because it is usually forgotten in pricing: a key management
service, separate encrypted storage, malware scanning, its own backup and
restore drills, periodic access reviews, and its own share of penetration
testing and incident response.

## Open decisions before commissioning

1. **Storage provider** — same host as the application, or deliberately
   elsewhere so a host compromise is not a document compromise.
2. **Key management service**, and **who owns the keys** — the client, the
   vendor, or split. This determines whether the vendor can read documents, and
   it is a commercial and legal question rather than a technical one.
3. **Is the accountant transfer portal in scope?**
   `accountant-data-handoff.md` describes a controlled transfer route; building
   it into the vault is defensible but materially widens the project.
4. **Which document classes**, per the necessity assessment. The answer may be
   fewer than the client first asks for, which is a good outcome.
5. **Retention per class**, feeding the engine in phase 5.

None is an engineering decision.

## Related

[`document-storage-boundary.md`](document-storage-boundary.md) ·
[`accountant-data-handoff.md`](accountant-data-handoff.md) ·
[`certificate-upload-design.md`](certificate-upload-design.md) ·
[`../security/jober-data-retention-proposal.md`](../security/jober-data-retention-proposal.md) ·
[`../security/jober-processor-dpa-requirements.md`](../security/jober-processor-dpa-requirements.md) ·
[`../deployment/production-readiness.md`](../deployment/production-readiness.md)
