# ADR 0021: Stage B shared-core extraction (in-place, sliced)

Status: **Accepted — activated 2026-07-07**
Date drafted: 2026-07-05 · Date activated: 2026-07-07

Supersedes [ADR 0001](0001-jober-only-scope.md) as of activation; satisfies
the sequencing recorded in [ADR 0020](0020-white-label-platform-sequencing.md).

## Activation trigger (as drafted) and the recorded waiver

As drafted, activation required **both**: (1) Jober accepts the demo, and
(2) the owners confirm starting platform work now.

**Owner decision, 2026-07-07:** condition (2) is confirmed and condition (1) is
**consciously waived** — Stage B starts before the Jober demo. Safety measures
adopted with the waiver: the pre-extraction state is tagged **`pre-stage-b`**
(demo-day fallback: check out the tag and rebuild); the running demo container
is left on its pre-extraction image until slice B5 validates; every slice keeps
the full test suite green with **unchanged assertions** (Stage D bar).

## Execution deviations recorded at activation

- Moved apps keep their **directory basenames** so Django's derived app labels
  (and therefore migrations/FKs/tables) are untouched — e.g. `core/projects`,
  `features/finance`, not the matrix's cosmetic target names.
- The physical sub-splits (logistics → accommodation/equipment/transport;
  trials out of projects) are **deferred to Stage C prep** (they require
  `SeparateDatabaseAndState` label surgery); until then sub-features are gated
  by `FEATURE_FLAGS` keys.
- `core/tasks` is not built (per this plan's own conditional); B4 delivers
  **retention** and **stdlib TOTP 2FA** (off for Jober by default).

## Context

Jober is feature-complete (Phases 0–4; 226 unit + 16 e2e tests; demo-ready). The
white-label strategy — one shared codebase, Jober and CorvinumEU as the first two
clients — is decided (ADR 0020; CorvinumEU design §12.4–12.5). The planning half
of Stage B is done: the [extraction matrix](../platform/extraction-matrix.md) is
completed against the real repository (2026-07-05 sweep) and the
[extraction plan](../platform/extraction-plan.md) stages the execution. The sweep
found the core→feature coupling **one-directional and localized** (three call
sites plus the dashboard), which keeps the §12.5 estimate (~2–3 weeks) credible.

## Decision (effective on activation)

1. **The platform is built by evolving HR_System in place** — no fork, no fresh
   repo. History, CI, hash-pinned locks, and the test safety net stay intact.
2. **Execution follows the extraction plan's slices B0–B5**, one PR per slice,
   full suite green per slice, in the established branch→PR→merge workflow.
3. **Target layout** is the design doc §12.4 shape: `core/` (client-agnostic
   spine) + `features/` (per-client-switchable modules) + `clients/` (settings,
   policies, theme, seeds) + `deploy/`.
4. **Build discipline (non-negotiable):** dependencies point feature → core only
   (CI-checked from slice B0); the core never branches on client identity —
   client difference lives in `CLIENT_POLICIES` implementations and
   `FEATURE_FLAGS`; migrations preserve historical app labels and table names so
   the reshape needs **no data migration**.
5. **Acceptance bar** is Stage D (design doc §12.5): no client-specific
   conditional logic in core; every core change is a genuinely reusable
   capability; **Jober behavior is preserved, proven by the existing test suite
   passing with assertions unchanged**; both flag sets (Jober all-on, synthetic
   all-off) stay green.

## Consequences

- ADR 0001 is superseded **only at activation** — reviewers keep rejecting
  platform abstractions in the current build until then.
- During Stage B, product feature work for Jober is frozen or rebased carefully;
  the plan's slices are small enough to interleave with pilot support if needed.
- Stage C (CorvinumEU as the first thin client) becomes a config + theme +
  feature exercise on top of the extracted core; the corvinum.eu admin-component
  reuse audit (design doc §7.0) gates any component transplant.
- Supply-chain rules (AGENTS.md) are unchanged: Stage B introduces **no new
  runtime dependencies** — hooks and registries are stdlib + Django only.
- If activation is declined (Jober stops after the pilot), the matrix and plan
  remain shelf-ready documentation; nothing in the current build depends on them.
