# Source Register

Last updated: 2026-06-29

| Source | Authority | Phase 0 use |
|---|---|---|
| `AGENTS.md` | Highest authority for scope, security, supply chain, dependencies, and operating rules. | Binding. |
| `Product_Design.md` | Authoritative product/build baseline for Jober v3.1. | Phase 0 task list and acceptance. |
| `Handoff.md` | Entry brief and conflict-order summary. | Confirms Phase 0 only. |
| `Finance_Specs.md` | Authoritative finance detail for Phase 4. | Source only; no finance module in Phase 0. |
| `Messaging_Specs.md` | Messaging addendum; top banner supersedes old Telegram-bot content. | Source only; no provider integration in Phase 0. |
| `demo/jober/` | Visual/workflow reference. | Useful for Jober look, folder-tab vocabulary, and mobile density. |
| `demo/internal/`, `demo/corvinum/` | Historical demo artifacts. | Non-authoritative. Do not copy Corvinum/shared scope into production. |
| `demo/demo_prototype_build_spec.md` | Historical static-demo spec. | Non-authoritative for production. |
| `docs/platform/extraction-matrix.md` | **Forward-looking planning** for the post-completion shared-core extraction (Stage B). Non-authoritative for the current build; see ADR 0020. | Not used; do not act on in current phases. |
| `docs/platform/corvinumeu-peopleops-design.md` | **Forward-looking planning** — second-client (CorvinumEU) product design. Non-authoritative for the current single-client Jober build; see ADR 0020. | Not used; do not act on in current phases. |

The mixed Jober/Corvinum architecture is historical background only. It must not drive code, data models, navigation, permissions, deployment, or client abstractions in the production app. The `docs/platform/` documents describe a **post-Jober-completion** platform strategy ([ADR 0020](../adr/0020-white-label-platform-sequencing.md)); they are planning inputs only and, per [ADR 0001](../adr/0001-jober-only-scope.md), do not authorise any platform/white-label/Corvinum code in the current build.
