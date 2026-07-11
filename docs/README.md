# Documentation index

**Naming convention:** unprefixed docs are **platform-shared**; client-specific
docs carry a `jober-` / `corvinum-` prefix (root specs: `Jober_` casing).
ADRs are the **single chronological decision log** for the whole platform —
they are never renamed or renumbered per client.

## Root specs
| Doc | Owner | Purpose |
|---|---|---|
| `../Jober_Product_Design.md` | Jober | Product truth: modules, workflows, plan §§ |
| `../Jober_Finance_Specs.md` | Jober | Finance module spec (positive sign convention, Q4) |
| `../Jober_Messaging_Specs.md` | Jober | SMS/Telegram messaging spec |
| `../AGENTS.md` | Platform | **Binding authority**: scope, security, supply chain |
| `../CLAUDE.md` | Platform | Session onboarding for coding agents |
| `../ENVIRONMENT.md`, `../Handoff.md`, `../README.md` | Platform | Environment/runtime notes, handoff, repo intro |
| `../BUILD_JOURNAL.md`, `../test_journal.md`, `../deployment_journal.md` | Platform | Newest-first journals (historical record; old doc names are kept as written) |

## docs/adr/ — Platform (shared decision log, 0001–0024)
Highlights: 0008 RBAC model · 0016 whitenoise · 0019 Twilio-via-stdlib ·
0020 white-label sequencing · 0021 Stage B extraction (EXECUTED) ·
0022 Stage C CorvinumEU thin client (EXECUTED) · 0023 payslips/encrypted PDF ·
0024 segno QR.

## docs/platform/ — Platform
| Doc | Purpose |
|---|---|
| `extraction-matrix.md`, `extraction-plan.md` | Stage B plan of record (executed) |
| `corvinumeu-peopleops-design.md` | CorvinumEU product design (v0.6) — CorvinumEU-owned content, platform-hosted |

## docs/deployment/
| Doc | Owner | Purpose |
|---|---|---|
| `deployment-plan.md` | Platform | Dokku/VPS deployment architecture for both clients |
| `production-readiness.md` | Platform | Static serving, gunicorn, image checks |
| `local-dev-db.md` | Platform | Dev Postgres container |
| `jober-local-demo.md` | Jober | Local demo runner (port 8000) |
| `jober-demo-runbook.md` | Jober | Presenter script (~60 min) |
| `jober-dokku-staging.md` | Jober | Staging skeleton (pending server names) |
| `jober-twilio-setup.md` | Jober | Twilio + Doppler secrets |
| `corvinum-demo-runbook.md` | CorvinumEU | Presenter script (~30 min, port 8001) |

## docs/permissions/
| Doc | Owner |
|---|---|
| `jober-permission-matrix.md` | Jober — mirrors `clients/jober/policies.py` |
| `corvinum-permission-matrix.md` | CorvinumEU — mirrors `clients/corvinum_eu/policies.py` |

## docs/product/
| Doc | Owner | Purpose |
|---|---|---|
| `playwright-test-environment-note.md` | Platform | e2e environment notes |
| `jober-phase1-open-questions.md`, `jober-phase3-4-open-questions.md` | Jober | Client Q&A rounds (answered) |
| `jober-open-decisions.md`, `jober-risk-blockers.md` | Jober | Open decisions / blockers |
| `jober-demo-inventory.md`, `jober-demo-to-django-map.md`, `jober-removed-feature-inventory.md`, `jober-source-register.md` | Jober | Build-era inventories and source register |
| `corvinum-open-questions.md` | CorvinumEU | C-Q1…C-Q16 build defaults awaiting client confirmation |

## docs/security/
| Doc | Owner | Purpose |
|---|---|---|
| `security-review-2026-06-29.md` | Platform | Security review record |
| `jober-blacklist-legal-basis.md` | Jober | Legitimate-interest basis; LIA pending |
