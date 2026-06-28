# Open Decision Register

Last updated: 2026-06-17

Phase 0 must not hardcode these into migrations or domain logic.

| Area | Decision needed | Current handling |
|---|---|---|
| Python lock | Exact package pins and hash-locked transitive dependency set. | Runtime and test locks generated in digest-pinned Python container. |
| Base image digests | Python runtime/build/test image digests. | `python:3.12-slim` resolved to `python@sha256:d764629ce0ddd8c71fd371e9901efb324a95789d2315a47db7e4d27e78f1b0e9`. |
| Tailwind binary | Trusted SHA-256 for Tailwind standalone CLI v4.3.0. | Resolved: official Tailwind Labs `tailwindcss-linux-x64` checksum is committed and Docker verifies the official release before execution. |
| Recruiter/coordinator read scopes | Whether GDPR/legal answer requires recruiter-scoped reads, broad internal reads, or another split for sensitive worker data. | **Answered 2026-06-28** (phase1-open-questions Q4): ordinary operational data stays broad-read; **sensitive fields** (DOB, health/disability, ID numbers) are visible to the owning recruiter + responsible coordinator(s) + all managers + all observers, and hidden from non-owning recruiters / non-responsible coordinators. Phase 1 builds per-field visibility for these. |
| Person fields | Exact remaining Person and WorkerProfile fields. | Not modeled in Phase 0. |
| Disability document | Meaning and storage requirement. | **Answered 2026-06-28** (phase1-open-questions Q1): **flag only** (yes/no), no documents scanned or uploaded. Optional disability *type* (§11.3) may be a simple field; no files either way. |
| Inactive reasons | Allowed catalog values. | Not modeled in Phase 0. |
| Project reassignment | Whether manager approval is required. | **Answered 2026-06-28** (phase1-open-questions Q2): **coordinator-driven** — no separate manager approval for assigning/reassigning a person to a project. (Initial activation to WORKING still runs through four-pillar readiness + manager approval, §12.4.) |
| Accommodation | Real list, rooms, capacities, rates, overrides. | Not modeled in Phase 0. |
| Inventory | Catalog, sizes, opening stock, purchase prices. | Not modeled in Phase 0. |
| Deduction review | Missing-returnable-item process. | Not modeled in Phase 0. |
| Finance sign convention | Whether costs are entered negative or stored positive and subtracted. | Phase 4 blocker; needs one filled month. |
| Legal/privacy | DPA, EU hosting approval, blacklist legal basis, employee-leasing documents. | Blocks real-data gate, not fictional Phase 0 shell. |
| Branding terminology | Final HU/SK/UA product wording and assets. | Base language is now English (ADR 0017); Slovak is the default rendering. EN/SK/HU/UK catalogs ship compiled, but HU/UK + revised SK are AI-authored and need a fluent-speaker review before client use. |
