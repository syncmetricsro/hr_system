# Legitimate Interest Assessment — blacklist / do-not-rehire

> **DRAFT. Not legal advice. Unsigned, and not a completed LIA until the
> client's data-protection adviser has reviewed, edited and signed it.**
>
> Written by the engineering side so a DPO edits rather than starts from blank,
> and so the technical safeguards are described accurately. Every control cited
> in §3.4 is implemented and named by file.
>
> Prepared 2026-08-03 · Processing: re-entry matching and do-not-rehire
> decisions (plan §11.14) · Controller: Jober · Basis claimed: GDPR Art. 6(1)(f)
>
> Stated basis and outstanding items:
> `docs/security/jober-blacklist-legal-basis.md`, which has recorded "a
> documented LIA" as required since **2026-06-30**. This is the older of the two
> outstanding assessments and it gates real-data use of the whole module.

## Why this one is harder than the offer-email LIA

Three features of this processing raise the bar, and the DPO should hold them in
view throughout:

1. **The consequence is exclusion from work** — the most severe outcome the
   system can produce for a person.
2. **The data subject is typically unaware.** A blacklisted person is not
   notified, and a re-entry match happens during someone else's intake.
3. **It processes a new data element collected for no other purpose** — the
   mother's maiden name, used only to build a matching fingerprint.

## 1 · Purpose test

**The processing.** Two linked activities. First, recording a manager-approved
decision that a specific reviewed person should not be re-engaged. Second,
matching a new intake against those decisions so a previously excluded person is
flagged rather than silently re-hired.

**The interest**, as stated by the client on 2026-06-30, on three grounds:

- **Fraud prevention** — protecting the business from a person previously found
  to have acted fraudulently.
- **Security vetting** — protecting the existing workforce and client sites.
- **Hiring decisions** — running recruitment on an informed basis.

The first two are strong and well recognised. The third is weaker and closer to
ordinary commercial preference; if the balance is contested, grounds one and two
are what carry it. **The DPO may wish to narrow the stated purpose to fraud and
safety only**, which would also narrow the acceptable reason categories.

**Would it be unlawful not to do it?** No, but there is a real duty-of-care
argument for grounds one and two that has no equivalent in the offer-email
assessment — re-engaging someone previously removed for a safety incident
creates risk for other workers.

## 2 · Necessity test

**Does it achieve the purpose?** Yes. Without it, re-entry under a variant
spelling or a different office is undetectable at scale.

**Less intrusive alternatives?**

- *Rely on recruiter memory.* Fails across three offices and over years, and is
  less fair, not more: it produces inconsistent, unrecorded, unchallengeable
  exclusions. **A documented process is arguably better for the data subject
  than the informal one it replaces**, and that point belongs in the balance.
- *Store names only.* Weaker matching and **more** intrusive — plain names are
  readable by anyone with database access, where the current design stores only
  hashes.
- *Store the raw identifier.* Rejected in the build. Matching works on a keyed
  HMAC, so a database compromise yields no identifiers.
- *Shorter retention.* Genuinely available and recommended — see
  `jober-data-retention-proposal.md`, which proposes reducing the 5-year
  placeholder to 3.

**Is the composite fingerprint necessary?** This is the sharpest necessity
question. Alongside the optional ID hash, the system hashes a canonical
composite of name tokens + date of birth + **mother's maiden name**. The
justification is that ID codes are often absent, and name+DOB alone false-matches
across a workforce with many shared names. The maiden name is collected
transiently for hashing and never stored in any form. **The DPO must decide
whether that added element is proportionate**, since it is data collected for no
purpose other than this one.

## 3 · Balancing test

### 3.1 Reasonable expectations

A candidate would reasonably expect an agency to keep a record of why an
engagement ended and to consider it if they reapply. That expectation is
narrower than the implementation in two ways:

- They would not necessarily expect a **cross-office, company-wide** record. The
  blacklist is a deliberate exception to office scoping — a person blocked at
  one office is caught at all three.
- They would not expect their **mother's maiden name** to have been used to
  build a durable matching token.

### 3.2 Likely impact

**High, by design** — the outcome is exclusion from work, and for this population
that is loss of income. Two mitigations bear directly:

- The exclusion is not automatic. A match produces a *proposed* case that a
  manager must decide (§3.4). The system flags; a human excludes.
- The reason is restricted, not broadcast: the *existence* of a case is visible
  to recruiter/coordinator/manager, but the **reason and category** require
  `blacklist.view_reason` (coordinator + manager only).

The residual risk is a **false match** — a different person sharing a name, date
of birth and maiden name. Mandatory manager review is the control; the reviewer
must be told this explicitly, because a system-generated match reads as
authoritative.

### 3.3 Vulnerability, and the transparency problem

Same population and dependence as the offer-email assessment (§3.3 there), plus
two problems specific to this processing:

- **The subject is not told.** There is no notification on blacklisting and none
  on a re-entry match. This is the biggest gap in the balance.
- **Objecting is therefore near-impossible in practice.** Art. 21 gives an
  absolute right to object to legitimate-interest processing; a person who does
  not know a case exists cannot exercise it. A manager can remove a case with a
  reason, but only if someone asks.

**The DPO should decide what the person is told and when.** Options run from
"stated in the privacy notice only" to "informed on decision". This is a policy
choice with a real operational cost, and engineering has deliberately not
pre-empted it.

### 3.4 Safeguards actually implemented

Verified against the code on 2026-08-03.

| Safeguard | Where | Effect |
|---|---|---|
| **No raw identifier is ever stored** | `compute_fingerprint` → keyed **HMAC-SHA256**; `MatchFingerprint` holds hash + `key_version` only | A database compromise yields no identifiers, only hashes |
| **Key rotation without re-hashing** | `BLACKLIST_HMAC_KEYS`, newest last; `key_version` indexes it | A leaked key can be retired |
| **Maiden name never persisted** | hashed transiently in `compute_composite_identifier` | Not a person field, intake answer, or audit value |
| **Warning, never silent exclusion** | a match creates a `PROPOSED` case; `decide_case` requires `PROPOSED` and a manager | The system flags; a human decides |
| **Activation hard-gated while unresolved** | open case blocks activation | An undecided case cannot be bypassed by carrying on |
| **Restricted reason** | existence broadly visible; reason/category behind `blacklist.view_reason` | The stigmatising detail is not broadcast internally |
| **Decisions are manager-only and reasoned** | `blacklist.decide`; removal also requires a reason | Every state change has an accountable actor |
| **Full audit trail** | propose / decide / remove and every lifecycle change appended; **no raw identifier in metadata** | Reconstructable without re-exposing the identifier |
| **Execution gate** | `BLACKLIST_MATCHING_ENABLED`, checked at both match call sites | Matching can be switched off pending approval, per plan §11.14 |
| **Retention with a purge that runs** | `expires_at` = today + `BLACKLIST_RETENTION_DAYS`; `purge_expired` deletes past-expiry fingerprints | Hashes age out — unlike most stores in this system |

**Not implemented, and relevant:**

- **No notification to the data subject** at any point (§3.3).
- **`BlacklistCase` rows have no expiry** — only fingerprints are purged, so the
  free-text reason, the more sensitive artefact, currently outlives the hash.
  This looks like an oversight rather than a decision; see the retention
  proposal, row 3.
- **No structured appeal path.** Removal is a manager action, not a process a
  person can initiate.
- The reason categories are seeded placeholders and **some could touch
  special-category data** (health, criminal allegations). Art. 9 would then apply
  and Art. 6(1)(f) alone would not be enough. **The category list must be
  reviewed before real use** — this is called out in the existing basis document
  and is not resolved.

## 4 · Outcome

**Engineering's reading: the technical design is unusually protective — hashes
rather than identifiers, mandatory human decision, restricted reasons, a working
purge — but the transparency position is weak, and that is where an assessment
would fail rather than on the data handling.**

Unresolved, none of them engineering decisions:

1. What the data subject is told, and when (§3.3).
2. Whether the mother's-maiden-name composite is proportionate (§2).
3. Whether the reason-category list stays clear of Art. 9 data (§3.4).
4. Whether the stated purpose narrows to fraud and safety, dropping the general
   hiring-decisions ground (§1).
5. The retention period, currently a 5-year placeholder (§2, and the retention
   proposal).

If the assessment is to be narrowed rather than rejected, the cheapest
meaningful changes are: shorten retention, give cases the same expiry as their
fingerprints, and add a notification step.

## 5 · Review and sign-off

Reassess if: the reason categories change; matching is extended to new
identifiers; retention changes; notification is introduced; or a decision is
challenged by a data subject.

| | Name | Role | Date | Signature |
|---|---|---|---|---|
| Prepared (engineering draft) | | | 2026-08-03 | — |
| Reviewed | | Data-protection adviser / DPO | | |
| Approved | | Client business owner | | |

**Until signed, matching stays on fictional data with the execution gate
available. This document does not open the real-data gate.**
