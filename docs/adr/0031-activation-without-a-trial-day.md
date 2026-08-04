# ADR 0031: Activation without a trial day, and self-approval in a single-admin office

Status: **Accepted — 2026-08-04.**
Date drafted: 2026-08-04

## Context

Two complaints from the client, with one root cause: **an office may have
exactly one administrator**, and the activation workflow was designed assuming
at least two people and always a trial day.

### 1 · Activation was unreachable without a trial

Readiness — and therefore activation — only opened after a trial was scheduled
*and* passed. For a worker the office already knows, or one returning after a
break, the trial day is a detour that produces no information.

Reading the code first changed the size of this problem considerably. **No
service in the activation chain ever required a trial.**
`get_or_create_readiness`, `update_readiness`, `_assert_ready`,
`request_activation` and `activate_on_project` never reference `Trial`. Both
clients already permitted `AVAILABLE → WORKING` in `ALLOWED_TRANSITIONS` —
Jober's entry even carries the comment `# CARGO manager override / direct
activation`, and `activate_on_project`'s docstring anticipates exactly this
override. `readiness_update` and `activate_person` accept any project pk and
never check it against a trial.

The requirement lived in one derived flag on the person page
(`in_readiness`, which demanded `TRIAL_DAY` plus a passed trial) and in the
template sourcing its project from `passed_trial.project.pk`. It was a
presentation constraint that read like a business rule.

### 2 · A single manager could never decide their own request

`decide_activation` refused when the decider was the requester, and the view
turned that into a 403. Confirmed live on CorvinumEU staging: one manager, two
pending approvals, both raised by that manager, neither ever decidable —
`/hu/activations/2/decide/` answered 403 with no explanation.

The control was added deliberately (plan §12.4, production-readiness item 14)
and the reasoning was sound: a manager holds both `project.assign` and
`approval.activate`, so the role gate alone gives no separation of duties. What
it did not account for is an office with nobody else to ask. There the rule does
not make activation stricter; it makes it **impossible**.

## Decision

### The trial is waivable; readiness is not

A new manager-only action, `activation.waive_trial`, opens readiness on an
Available person for a chosen project without any trial. `ReadinessRecord`
gains `trial_waived`, and `core/projects/services.py::waive_trial` sets it.

**The four pillars still gate activation.** `_assert_ready` is untouched, so
medical and gear must still be complete and the entry medical date is still
recorded. Waiving a trial day is an operational shortcut; waiving the entry
medical certificate would be a labour-law problem in SK and HU, and it would
surface later as compliance-dashboard alerts on workers already on site. The
distinction is the whole point of the change and `test_trial_waiver.py` exists
mainly to keep it from eroding.

**The person stays Available** until the decision. Moving them to Trial-day
would make the lifecycle claim a trial that never happened, and
`AVAILABLE → WORKING` is already a permitted transition in both clients.

The flag is stored rather than derived because the readiness panel has to
survive the redirect, and because the record should carry its own answer to
"did this worker ever do a trial?". `exit_person` clears it: a waiver is spent
once used, and leaving it set would reopen the readiness panel the moment the
worker is recycled to Available.

**Manager-only, and a new action rather than a reuse.** `readiness.complete` was
the obvious candidate, but coordinators hold it in both clients and this must
not be theirs.

### Self-approval is allowed, and recorded

`SelfApprovalError` is gone, along with the view's 403. `decide_activation` now
computes `self_approved` and adds it to the audit event **only when true**, so
the ordinary two-person decision stays quiet and a search for self-approvals
returns exactly them. The activation queue labels the row so the manager sees
what they are about to do.

The separation-of-duties control therefore becomes **visibility rather than
prevention**. That is a genuine reduction in strength and it is the point: a
control that makes the product unusable gets worked around or switched off
entirely, and neither leaves a record. This one leaves a record.

Both changes apply to Jober and CorvinumEU. Both live in `core/`, so each is
implemented once; the action is granted to `_MANAGER` in each client's
`policies.py` and mirrored in both permission matrices.

## Consequences

**The two stuck CorvinumEU staging approvals unblock on deploy.** No data fix is
needed — they were only ever blocked by the runtime check.

**An auditor's question now has an answer.** "Which activations had no second
pair of eyes?" is a query against `AuditEvent.metadata`, where before the answer
was "none, by construction" and, on staging, "none, and also no activations at
all".

**Trial-day statistics stay honest.** No synthetic `TrialAssignment` row is
created for a waived activation, so any future "trial pass rate" is not diluted
by trials that never happened. The cost is that `trial_waived` must be consulted
to tell "activated without a trial" from "activated after a trial".

**This is a relaxation, and it should be revisited if the offices grow.** If
Jober or CorvinumEU staff a second administrator per office, requiring a
distinct decider again becomes reasonable — and the audit metadata added here is
what would show whether self-approval was still being relied on.

## Not doing

- **A single "activate now" button** from Available to Working. It would bypass
  medical and gear entirely. The readiness form is three fields, and the
  compliance dashboard would flag the result anyway.
- **A per-client `ALLOW_SELF_APPROVAL` policy key.** It would be `True` in both
  clients today; a switch with one position is not a switch.
- **Allowing self-approval only when no other manager exists in the office.**
  Wrong the moment the second manager is on holiday, and it makes a permission
  outcome depend on staffing data.
