# Demo-To-Django Map

Last updated: 2026-06-17

| Demo surface | Production treatment |
|---|---|
| Jober folder tabs | Keep as a design reference for top-level navigation. |
| Dashboard shell | Recreate as server-rendered Django template with Jober-only content. |
| Mobile manager/field view | Rework into coordinator mobile field mode with htmx full-page fallback. |
| Role switch | Replace with authenticated Django users and server-side role checks. |
| Language switch | Replace with Django localization, HU/SK/UA only. |
| People roster/risk check | Later Person/intake/duplicate/blacklist services; no Phase 0 model. |
| Approval story | Later readiness and manager activation workflow. |
| Shift/SMS/sick/certificate story screens | Do not migrate as-is; map only confirmed concepts such as SMS and entry-medical dates. |
| Accommodation and equipment | Later logistics modules with real models and audit. |
| Pohoda/accounting mock | Remove; later manual finance oversight per `Jober_Finance_Specs.md`. |
| In-memory state | Replace with PostgreSQL, forms, services, and audited state transitions. |
