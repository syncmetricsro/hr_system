# Phase 1 — Open Questions for Jober

Created: 2026-06-24 · Answers recorded: 2026-06-28 (all four answered)

Decisions needed from Jober before (or early in) the Phase 1 business build.
Most of Phase 1 is already specified in `Jober_Product_Design.md`; only the four below
genuinely shape the data model or workflow logic. Each has a safe default we will
use (flagged as an assumption) if no answer arrives, so the build is not blocked.

Record the answer and date on each line as they come in.

## Tier 1 — needed to finalize the model/logic

### 1. Disability / reduced working ability — how much to store?
When a worker states during intake that they have a disability or reduced working
ability, how much should the system keep? Just **yes/no and the type**, also a
**note that an official document exists**, or the ability to **upload and store
the actual document file**?
- Why it matters: storing health documents adds legal/privacy duties; we build only what's needed.
- Plan ref: §11.3 (explicitly refuses to guess "type + document").
- Safe default: metadata only (yes/no + type); no document archive.
- **Answer (2026-06-28): Flag only.** Record disability as a yes/no flag; **no documents scanned or uploaded**. (An optional disability *type* per §11.3 may be captured as a simple field; no files either way.)

### 2. Who can place a worker on a project?
Can a **recruiter/coordinator** assign or move a worker to a project on their own,
or must a **manager always approve** the placement?
- Why it matters: decides whether there is an approval step (and possible bottleneck) in daily flow.
- Plan ref: §12.5 ("authorized user"); open-decisions "Project reassignment".
- Safe default: recruiter recycles an Available person freely; reassigning a *Working* person needs manager approval.
- **Answer (2026-06-28): Coordinator.** The coordinator places/reassigns workers to projects; the manager does **not** confirm each coordinator action (manager has oversight/visibility instead). See "Additional requirement" and "To clarify" below.

### 3. Real personal data now, or test data first?
Build secure handling of **real personal ID data** (ID-card / passport numbers)
**now**, or keep using **made-up test data** and add real-data handling **later,
once legal / GDPR approvals are in place**?
- Why it matters: real personal data must not enter before the legal paperwork; this confirms timing and how much security scaffolding to build now.
- Plan ref: §11.2 (PersonIdentifier), Handoff real-data gate.
- Safe default: model the fields + masking now; defer encryption/HMAC matching to the real-data gate; fictional data only until then.
- **Answer (2026-06-28): Test data first.** Confirms the safe default — model fields + masking now, defer encryption/HMAC to the real-data gate, fictional data only.

### 4. Who may see sensitive personal details?
Who within the company may see **sensitive fields** — date of birth, health /
disability info, ID numbers? The **whole internal team**, or only **certain roles**
(e.g. managers and the recruiter who entered the person)?
- Why it matters: internal reads are broad by default, but these specific fields may need limiting.
- Plan ref: §8.1 (covers identifiers + blacklist/feedback; health visibility unspecified). Ties to the open GDPR read-scope (`BROAD_INTERNAL_READS`).
- Safe default: identifiers masked (already); disability/health restricted to manager + owning recruiter.
- **Answer (2026-06-28, clarified): Owning recruiter + responsible coordinator + all managers + all observers.** Sensitive fields (DOB, health/disability, ID numbers) are visible to: the recruiter who entered the person, the person's responsible coordinator(s), every manager, and every observer. They are hidden only from recruiters who did not enter the person and coordinators not responsible for them.

## Additional requirement raised (2026-06-28)

- **Manager alert system** — managers need to be alerted when a person's papers/
  documents are **missing or about to expire**. Maps to the planned compliance
  alerts (§11.9; reconciled 11/23-month alerts), which are roadmap **Phase 3**.
  Phase 1 groundwork: store the relevant dates (entry-medical date, certificate
  expiry metadata) and surface "missing" via the readiness view, so the alert
  layer plugs in later without rework.

## Resolved (2026-06-28) — Activation gate

**Coordinator activates; the system enforces the readiness gate.** A worker
becomes `WORKING` when the coordinator activates them, and the **system blocks**
activation unless the required pillars are satisfied (medical + gear always
required; accommodation + transport may be N/A with reason). There is **no manual
manager-approval step** — the manager oversees via alerts (missing/expiring
papers), not by confirming each activation.

This **supersedes the manager-approval step in §11.6 / §12.4**: `ActivationApproval`
becomes an *activation record* (who activated, when, readiness snapshot) for audit
rather than a manager approve/reject gate; the "manager approval button" becomes a
coordinator "activate" action that is disabled until required pillars resolve. The
**CARGO manager override** (§11.6) still stands. An ADR will formalize this at
implementation.

## Tier 2 — buildable around (configurable; not blocking)

Built as data-driven catalogs/engines now; Jober supplies the values later:
exact remaining **Person/WorkerProfile fields**, **Inactive reasons** catalog,
localized **typed-negative phrases**, full **intake questionnaire content**.

## Not blocking code (go-live only)

DPA / EU hosting / blacklist legal basis / employee-leasing documents, and the
**finance sign convention** (Phase 4). Real PII stays out until the legal gate.
