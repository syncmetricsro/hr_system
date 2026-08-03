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
| `../Jober_Messaging_Specs.md` | Jober | Reconciled Twilio SMS status and Telegram channel-broadcast entrypoint |
| `../AGENTS.md` | Platform | **Binding authority**: scope, security, supply chain |
| `../CLAUDE.md` | Platform | Session onboarding for coding agents |
| `../ENVIRONMENT.md`, `../Handoff.md`, `../README.md` | Platform | Environment/runtime notes, handoff, repo intro |
| `../BUILD_JOURNAL.md`, `../test_journal.md`, `../deployment_journal.md` | Platform | Newest-first journals (historical record; old doc names are kept as written) |

## docs/ root
| Doc | Owner | Purpose |
|---|---|---|
| `i18n-workflow.md` | Platform | How to edit/compile/add/retrieve template & code translations (SK/HU/UK) |
| `i18n-seeded-data.md` | Platform | How seeded catalog data stays localized (db_trans + catalog_i18n) |
| `session-summary-2026-07-16.md` | Platform | Consolidated product, demo, staging, testing, and remaining-gates handoff for the implementation session |

## docs/adr/ — Platform (shared decision log, 0001–0029)
Highlights: 0008 RBAC model · 0016 whitenoise · 0019 Twilio-via-stdlib ·
0020 white-label sequencing · 0021 Stage B extraction (EXECUTED) ·
0022 Stage C CorvinumEU thin client (EXECUTED) · 0023 payslips/encrypted PDF ·
0024 segno QR · 0025 Chart.js visualizations · 0026 office-scoped RBAC
(ACCEPTED, Phases A+B executed, amends 0008 — Jober multi-office;
staff-invitation subsystem deferred) ·
0027 Pillow for avatar images (ACCEPTED) · 0028 fpdf2 for the feedback flyer
(ACCEPTED).

## docs/platform/ — Platform
| Doc | Purpose |
|---|---|
| `extraction-matrix.md`, `extraction-plan.md` | Stage B plan of record (executed) |
| `client-feature-matrix.md` | Per-client feature/flag comparison |
| `corvinumeu-peopleops-design.md` | CorvinumEU product design (v0.6) — CorvinumEU-owned content, platform-hosted |

## docs/deployment/
| Doc | Owner | Purpose |
|---|---|---|
| `deployment-plan.md` | Platform | Dokku/VPS deployment architecture for both clients |
| `deployment-plan.md` | Platform | Dokku/VPS architecture, both clients, asks D1–D8 |
| `syncmetric-prime-staging.md` | Platform | Concrete staging runbook for the syncmetric-prime VPS |
| `production-readiness.md` | Platform | Static serving, gunicorn, image checks |
| `local-dev-db.md` | Platform | Dev Postgres container |
| `jober-local-demo.md` | Jober | Local demo runner (port 8000) |
| `jober-demo-runbook.md` | Jober | Presenter script (~60 min) |
| `jober-dokku-staging.md` | Jober | Staging skeleton (pending server names) |
| `jober-twilio-setup.md` | Jober | Twilio + Doppler secrets |
| `corvinum-demo-runbook.md` | CorvinumEU | Presenter script (~30 min, port 8001) |
| `avatar-upload-acceptance.md` | Platform | Shared fictional avatar formats, rejection, UI-consumer, and stored-WebP acceptance check |
| `certificate-upload-acceptance.md` | Platform | Shared fictional PNG/PDF, storage-boundary, multilingual, and cleanup acceptance check |

## docs/permissions/
| Doc | Owner |
|---|---|
| `jober-permission-matrix.md` | Jober — mirrors `clients/jober/policies.py` |
| `corvinum-permission-matrix.md` | CorvinumEU — mirrors `clients/corvinum_eu/policies.py` |

## docs/product/
| Doc | Owner | Purpose |
|---|---|---|
| `playwright-test-environment-note.md` | Platform | e2e environment notes |
| `avatar-design.md` | Platform | Worker/admin avatar design — fully implemented 2026-07-25, including illustrated per-role default art |
| `pill-system-design.md` | Platform | Worker status pill, certificate-validity icons, Compliance/Reviews nav badges — fully implemented 2026-07-24 |
| `certificate-upload-design.md` | Platform | Shared forklift/crane/welding upload, renewal/history, RBAC, validation, and emergency purge — implemented 2026-07-31 |
| `document-storage-boundary.md` | Platform | Metadata-only/prohibited high-risk document boundary and optional separately scoped Secure Document Vault |
| `secure-document-vault-design.md` | Platform | Engineering design for the deferred, separately priced vault — architecture, data model, integration seam, phasing. **Designed, not built** |
| `secure-document-vault-proposal.md` | Platform | Client-facing offer for the same module: what it adds, what the client must supply, why it is priced apart (C-Q18) |
| `accountant-data-handoff.md` | Platform | Separate Slovak/Hungarian accountant handoffs: country-specific payroll facts and tax declarations, medical/ID exclusions, secure routing, and refusal of mixed/unresolved jurisdictions |
| `feedback-flyer-design.md` | Platform | Downloadable PDF+QR flyer for feedback links, Cyrillic-capable via a vendored font (ADR 0028) — implemented 2026-07-24 |
| `help-area-design.md` | Platform | Image-rich, feature-aware Help: exactly 12 workflow articles per client, client-specific fictional screenshots, shared article structure and complete SK/HU/UK catalogs |
| `notification-center.md` | Platform | Floating alerts/updates behavior, privacy, refresh, and extension contract |
| `client-themes.md` | Platform | Light/Dark/System behavior, client defaults, persistence, and palette ownership |
| `contextual-tooltips.md` | Platform | Hover/focus help, coverage, touch behavior, and content safety |
| `jober-phase1-open-questions.md`, `jober-phase3-4-open-questions.md` | Jober | Client Q&A rounds (answered) |
| `jober-open-questions-july-2026.md` | Jober | Handover-call questions (**open**); 4 of 6 block or reshape queued work |
| `jober-open-decisions.md`, `jober-risk-blockers.md` | Jober | Open decisions / blockers |
| `jober-client-ask-list.md` | Jober | **One page to take to the client** — every outstanding decision grouped by who answers it (lawyer / vendor / business) and what each one blocks |
| `jober-multi-office-scoping.md` | Jober | Multi-office (Velký Meder/Győr/Dunajská Streda) RBAC impact analysis — implemented (Phases A+B); only the staff-invitation subsystem §3a remains design-only (revisits ADR 0008) |
| `jober-offer-email-design.md` | Jober | Job-offer emails: per-language templates, per-person panel and capped bulk send (ADR 0029, implemented) |
| `jober-telegram-channel-design.md` | Jober | Canonical Manager/Admin-only, outbound Telegram channel-broadcast design — approved direction, not implemented, client/privacy gates open |
| `jober-demo-inventory.md`, `jober-demo-to-django-map.md`, `jober-removed-feature-inventory.md`, `jober-source-register.md` | Jober | Build-era inventories and source register |
| `corvinum-open-questions.md` | CorvinumEU | C-Q1…C-Q19 build defaults awaiting client confirmation |

## docs/security/
| Doc | Owner | Purpose |
|---|---|---|
| `security-review-2026-06-29.md` | Platform | Security review record |
| `jober-blacklist-legal-basis.md` | Jober | Legitimate-interest basis; LIA pending |
| `jober-blacklist-lia.md` | Jober | **Draft LIA** for do-not-rehire matching — unsigned, needs DPO review; the oldest outstanding legal gate |
| `jober-offer-email-lia.md` | Jober | **Draft LIA** for job-offer outreach — unsigned, needs DPO review |
| `jober-data-retention-proposal.md` | Jober | Inventory of every personal-data store with proposed periods and reasoning; records that only 2 of 10 stores have any purge path |
| `jober-processor-dpa-requirements.md` | Jober | What each Art. 28 agreement must cover, per processor (FORPSI hosting + SMTP, Twilio); none received |

| `jober-offer-email-legal-basis.md` | Jober | Legitimate-interest basis for job-offer outreach; opt-out implemented, LIA + DPA + retention period pending |
