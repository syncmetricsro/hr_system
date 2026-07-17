# Blacklist — legal basis & data handling

**Status: legal basis stated; written text + LIA pending. Real-data execution is
gated until sign-off — the module runs on fictional data only (`AGENTS.md`).**

## Legal basis (stated by the client, 2026-06-30)

**Legitimate interest** (GDPR Art. 6(1)(f)), on three grounds:

- **Fraud prevention** — legitimate interest in protecting the business.
- **Security vetting** — legitimate interest in protecting the workforce/clients.
- **Hiring decisions** — legitimate interest in running recruitment.

Legitimate interest (not consent) is the appropriate basis for a do-not-rehire
list: it is not withdrawable at will, and it fits fraud-prevention / security use.

## Still required before real-data use

- **The written text** — the annual worker contract with GDPR/personnel-data
  clauses (promised, not yet delivered) — to confirm transparency wording.
- **A documented Legitimate Interest Assessment (LIA)** — the three-part balancing
  test (purpose, necessity, balancing against data-subject rights), signed off by
  the lawyer/DPO. Naming the grounds above is the input to the LIA, not the LIA.
- Confirmation of the **retention period** (placeholder: `BLACKLIST_RETENTION_DAYS`
  ≈ 5 years) and the **reason-category list** (seeded with neutral placeholders;
  some categories can touch special-category data and need review).

## How the implementation minimises risk (plan §11.14 / §12.13)

- **No raw identifier is ever stored.** Matching uses a keyed **HMAC-SHA256** of a
  transiently-entered ID (`apps.blacklist.services.compute_fingerprint`); only the
  hash + `key_version` are persisted (`MatchFingerprint`). Keys rotate via
  `BLACKLIST_HMAC_KEYS` without re-hashing.
- **Secondary composite fingerprint (2026-07-17; LIA must cover it).** Alongside
  the optional ID hash, a second fingerprint type hashes a canonical composite
  of name tokens + date of birth + **mother's maiden name**
  (`compute_composite_identifier`). The maiden name is a *new data element*
  collected transiently for hashing only — never stored as a person field,
  intake answer, or audit value. The pending LIA and the written contractual
  language must describe this composite (data categories, purpose, the
  false-match risk being mitigated by mandatory manager review of every
  proposed match, and retention identical to ID fingerprints).
- **Data minimisation** — the `Person` record gains no identifier field.
- **Warning, not silent merge** — a match creates a *proposed* case for manager
  review; it never auto-blacklists or merges records. Activation is hard-gated
  while a case is unresolved.
- **Restricted reason** — the *existence* of a case (the flag / `BLACKLISTED`
  status) is broadly visible to recruiter + coordinator + manager; the **reason
  and category** are visible to **coordinator + manager only**
  (`blacklist.view_reason`). Decisions (approve/reject/remove) are manager-only
  (`blacklist.decide`).
- **Auditability** — propose / decide / remove and every lifecycle change are
  written to the append-only audit log; no raw identifier appears in audit
  metadata.
- **Retention** — fingerprints/cases carry an expiry; `manage.py purge_blacklist`
  drops expired hashes.
- **Execution gate** — `BLACKLIST_MATCHING_ENABLED` gates the matching check per
  §11.14 ("legal basis and retention must be approved before production
  execution").
