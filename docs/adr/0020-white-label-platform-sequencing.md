# ADR 0020: White-label platform sequencing (single-client now, extract later)

Status: Accepted
Date: 2026-06-29

Complements — does **not** supersede — [ADR 0001](0001-jober-only-scope.md).

## Context

Syncmetric's longer-term intent is a **white-label staffing-HR platform**: one
shared core plus thin per-client layers (features + theme + config), rather than
bespoke per-client systems. Jober is the first client; **CorvinumEU** is the second.

[ADR 0001](0001-jober-only-scope.md) mandates that the current production app be
**single-client Jober** with no client switching, no Corvinum references, no
white-label abstractions, and no shared-client data models. `Jober_Product_Design.md`
§3.3 reinforces this and marks the mixed Jober/Corvinum "shared platform" material
as historical, non-authoritative background.

The platform strategy is therefore **sequential, not concurrent**: finish Jober
first → extract the shared core from the finished Jober codebase → build CorvinumEU
as the first thin client. Two forward-looking planning documents now live under
`docs/platform/` to steer that later work:

- `docs/platform/extraction-matrix.md` — labels every Jober artifact (core /
  feature / client-policy / theme-ui / infra / obsolete) for the extraction.
- `docs/platform/corvinumeu-peopleops-design.md` — the second client's product
  design (added when its full text is supplied).

## Decision

- The current build **remains single-client Jober**. ADR 0001 stays in force; this
  ADR does not relax it. No client-switching, white-label abstraction, feature
  registry, or shared-client data model lands in the codebase now.
- The **shared-core extraction is a distinct later stage** that begins **only after
  Jober is complete**. It is out of scope for every current phase.
- The `docs/platform/` documents are **planning inputs for that later stage** and
  are **non-authoritative for current code**. They are registered as such in
  `docs/product/jober-source-register.md`.
- When the extraction stage actually starts, a **follow-up ADR will flip the
  scope** (superseding ADR 0001). Until that ADR is Accepted, ADR 0001 governs.

## Consequences

- Reviewers can reject any PR that introduces platform/white-label/Corvinum code
  into the current build by citing ADR 0001; this ADR removes the ambiguity that
  the `docs/platform/` docs might otherwise create.
- The extraction matrix and CorvinumEU design are maintained as **living planning
  docs**, kept in sync with the real Jober repo but never driving current code.
- The extraction estimate stays honest: the matrix's open flags (advances vs.
  Jober financials overlap, equipment on both clients, auth/RBAC compatibility,
  core-importing-feature coupling) are tracked as pre-extraction risks, not
  resolved by this decision.
