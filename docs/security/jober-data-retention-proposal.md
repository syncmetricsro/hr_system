# Jober — data retention proposal

> **DRAFT for client and DPO decision. Nothing here is approved.** Periods
> marked *proposed* are engineering suggestions with reasoning, offered so the
> conversation starts from something concrete. They are not legal advice and
> carry no authority until the client and their adviser set them.
>
> Prepared 2026-08-03. Fictional data only — the real-data gate is closed
> (`AGENTS.md`).

## Why this document exists

Several parts of the build are gated on "an approved retention period" and there
has never been a document saying what those periods should be, or even a list of
what stores personal data. Three separate places record the same blocker:
`docs/security/jober-blacklist-legal-basis.md`, `Jober_Messaging_Specs` §2, and
the deployment plan's real-data gate.

## The finding that matters most

**The retention framework exists and almost nothing uses it.**
`core/retention/services.py` provides `register_retention(name, purge_fn)` and a
single `run_retention` command that executes every registered job. Exactly two
features register:

```
features/feedback/apps.py    register_retention("feedback", purge_feedback)
features/blacklist/apps.py   register_retention("blacklist_fingerprints", purge_expired)
```

Everything else in the table below has **no purge path at all** — not a
misconfigured one, an absent one. For those stores, setting a period is a code
change and not only a decision.

One clarification, because the name is misleading:
`features/compliance/services.py::purge_certificate_files` is the **manager's
emergency single-file removal** (gated on `certificate.purge_file`, reason
required, audited). It is not retention and does not run on a schedule.

## Inventory

Personal-data stores, what governs them today, and what is proposed. "Decided"
means someone has actually approved it; everything else is open.

| # | Store | Personal data held | Today | Status |
|---|---|---|---|---|
| 1 | `FeedbackSubmission` | free-text worker message, optional rating | `FEEDBACK_RETENTION_DAYS = 31`, registered, purged | plan §11.11 says ≈1 month — **confirm** |
| 2 | Blacklist `MatchFingerprint` | keyed HMAC only; **no raw identifier** | `BLACKLIST_RETENTION_DAYS = 1825` (5y), registered, `purge_expired` deletes past `expires_at` | **placeholder pending approval** |
| 3 | `BlacklistCase` | category, free-text reason, decision, actor | no expiry; only fingerprints are purged | **open** |
| 4 | `OutboundEmail` (offer emails) | recipient address, subject, full body, language | `OFFER_EMAIL_RETENTION_DAYS = 0` = keep everything; registered, purge is a deliberate no-op | **open** (PR #157) |
| 5 | `OutboundMessage` / `InboundMessage` (SMS) | phone number, full message body | **nothing** — not registered, no purge | **open + code needed** |
| 6 | `Payslip` | net pay amount, period, delivery address, send timestamps | **nothing** | **open + code needed** |
| 7 | `AuditEvent` | actor, target person, action, reason text, metadata | **nothing**; the permission matrix says "retention follows the approved policy" — there is no policy | **open + code needed** |
| 8 | `Certificate` + uploaded files | licence metadata, scans of occupational certificates | **nothing** time-based | **open + code needed** |
| 9 | `Person` | name, DOB, place of birth, phone, email, address, nationality, disability flag/type, avatar | **nothing**; `archive` hides, it does not delete | **open + code needed** |
| 10 | Wage ledger / advances | monthly gross values, advances, deductions | **nothing** | **open + code needed** (CorvinumEU) |

Rows 5–10 are the substance of the ask: six stores of personal data with no
deletion path, including the two with the clearest statutory angle (payslips,
person records).

## Proposed periods, with reasoning

Each proposal names the hook it rests on. Where no hook is known, it says so
rather than guessing — a number invented here would be quoted back later as
though it meant something.

**1 · Feedback — keep 31 days (already set; confirm).** Operational triage only.
The purpose is answered within days; the value decays to nothing. Short
retention is also what the public submission form implies to the worker.

**2 · Blacklist fingerprints — proposed 3 years, currently 5.** The hook is the
period over which a re-hire decision is genuinely informed by a past event. Five
years is defensible for fraud but is at the long end for an employment context,
and the stored artefact is a hash rather than an identifier, which lowers the
argument for keeping it. **This is the single number most worth the lawyer's
attention**, because it is the one already coded and shipped as a placeholder.

**3 · Blacklist cases — proposed: same period as their fingerprints.** Today the
case row outlives the hash, which is the wrong way round: the free-text reason
is more sensitive than the hash and currently persists indefinitely.

**4 · Offer emails — proposed 12 months.** The body evidences what a worker was
told, which matters for a complaint or a dispute about terms offered. Twelve
months covers a plausible complaint window without accumulating a marketing
history. Deliberately left at `0` (keep everything) until decided, because
guessing destroys evidence.

**5 · SMS — proposed 12 months, same reasoning.** `Jober_Messaging_Specs` §2
already requires this before real-worker use; it has simply never been set.

**6 · Payslips — no proposal; statutory.** Slovak and Hungarian payroll
retention obligations govern this and neither is established in this repo. The
client's accountant will know the number. Note that Jober's payslip feature is
off; this is live for CorvinumEU.

**7 · Audit events — proposed 3 years, with a caveat.** The log is the control
that makes every other safeguard verifiable, so it should outlive the records it
describes. But it holds free-text reasons and person references, so
"indefinitely" is not automatically right either. **The append-only property
must survive whatever is chosen**: retention here means dropping whole aged
events on a schedule, never editing them.

**8 · Certificates — no proposal; tied to the document boundary.** Governed by
occupational-safety rules and by `docs/product/document-storage-boundary.md`.
Also interacts with C-Q7/C-Q13/C-Q16, already open for CorvinumEU.

**9 · Person records — no proposal; the biggest question.** Needs "kept for the
employment relationship plus N", and N is statutory. Today `archive` hides a
record from lists and keeps everything. That is defensible as long as a real
erasure path exists for an Art. 17 request — **there is none today**, which is
worth raising on its own.

**10 · Wage/advances — no proposal; statutory, as payslips.**

## What implementing any of this requires

- **A setting alone** is enough only for rows 1, 2 and 4 — the purge functions
  exist and are registered.
- **A purge function plus registration** is needed for rows 3 and 5–10. The
  pattern is small (`features/feedback/services.py::purge_feedback` is nine
  lines) but it is a code change per store, with tests.
- **`run_retention` must actually be scheduled.** The command exists; nothing in
  the deployment plan currently runs it on a timer. A retention policy that no
  cron executes is a policy on paper only.
- **Erasure on request (Art. 17) is not the same as retention** and is not built.
  Archive hides; it does not delete. Worth deciding separately.

## Sign-off

| | Name | Date |
|---|---|---|
| Proposed by (engineering) | | 2026-08-03 |
| Client business owner | | |
| Data-protection adviser / DPO | | |

Related: `jober-blacklist-lia.md`, `jober-offer-email-lia.md`,
`jober-processor-dpa-requirements.md`, and the consolidated
`docs/product/jober-client-ask-list.md`.
