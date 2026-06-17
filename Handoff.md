# Handoff Brief — Jober Production Build (for Codex / GPT-5.5)

Read this first, then the files below in order. The package was reconciled on 16 June 2026 so there is a single contradiction-free source.

## Authoritative files (priority order)

1. **`AGENTS.md`** (production folder root) — **governs scope, security, supply chain. Highest authority on those topics, and a primary input, not background.** All npm-free + Python-hardening rules live here, not in the plan.
2. **`jober_plan_v3.1_reconciled.md`** — the product/build plan, **now reconciled** with round-4 answers and the finance model. This **replaces** the older `_v3_jober_only` plan; use only this one. Authoritative for product/build.
3. **`finance_module_spec.md`** — the reverse-engineered finance model (categories, groups, calculations, two template bugs to avoid). Authoritative for finance line-item detail (Phase 4).
4. **`messaging_specification.md`** — Twilio SMS detail. **No Telegram bot** (existing manual channel); per-recipient selection; coordinator-scoped sending. Read its top banner.
5. **`jober_answers_round4.md`** — the raw resolved-inputs record behind the reconciliation. Reference if the plan's reasoning is unclear.

Conflict order: security/deps → `AGENTS.md`; product/scope → reconciled plan; finance detail → finance spec.

Older files now superseded (do **not** build from them): `jober_coding_agent_product_design_plan.md` (v1, React/Vite), `jober_coding_agent_product_design_plan_v3_jober_only.md` (pre-reconciliation), `discovery_round3_changes.md` (folded into the plan).

## Where to start

**Phase 0 only** — §30 "First coding-agent assignment" in the reconciled plan: repository skeleton, hardened local/CI/Docker setup, vendored+checksummed htmx/Alpine, pinned+verified Tailwind binary, corrected demo shell, ADRs. **Do not build business modules until Phase 0 passes its acceptance check**, which explicitly includes **no Node/npm/React/Vite artifacts**.

## Non-negotiable tripwires (from AGENTS.md)

- No Node/npm/React/Vite/`node_modules` anywhere in repo, build, or runtime.
- Python deps hash-pinned in a committed lockfile, hash-enforced install, cooldown on brand-new versions.
- Downloaded binaries (Tailwind CLI, Playwright browsers): pinned URL, **verify SHA-256 before executing, fail closed.**
- No secrets in Git; verify inbound webhooks (Twilio signature, Telegram secret token if ever used).
- No real worker PII before the real-data gate — fictional data only.

## Still-pending answers — build around them, don't invent

- **Finance sign convention** — the supplied Excel is the blank template; needs one *filled* month to confirm whether costs are negative inputs or `revenues − costs`. Build the finance structure but flag the sign as an assumption.
- **Lawyer items** — DPA, EU hosting approval, employee-leased-out document specifics, blacklist legal basis. None block coding on fictional data; all block real-data go-live.
- A handful of catalog details (Inactive reasons, accommodation/inventory opening data, remaining Person fields) — fill via configurable catalogs as each module is built; do not hardcode guesses.

## Real-state notes

- The reconciled plan's finance line items live in `finance_module_spec.md`, including two **real bugs in the manager's spreadsheet** the system must not reproduce (one project's costs under-summed; company total omitting two projects) — total dynamically over all projects and line items.
- "Office" is likely a non-concept for Jober; do not model it speculatively (see §28).