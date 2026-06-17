# Jober Workforce Management Platform
## Product Design and Coding-Agent Implementation Plan
### Jober-only, npm-free Django + htmx architecture

**Document version:** v3.1 (reconciled)
**Document status:** Authoritative implementation-planning baseline — incorporates round-4 client answers and the finance model. On any conflict, this file governs product/build; `AGENTS.md` governs security/supply-chain; `finance_module_spec.md` governs finance line-item detail.
**Date:** 16 June 2026
**Implementation owner:** SyncMetric
**Client/product scope:** Jober only
**Product owner:** To be designated by Jober

---

# 0. Purpose and source authority

This document defines the product and implementation plan for Jober's internal workforce-management platform.

It supersedes earlier planning wherever those documents conflict with:

1. the latest Jober interview change set (`Jober-2nd-interview-results.txt`, v0.4 delta);
2. the two recorded Jober manager interviews;
3. later written Jober decisions approved by the designated product owner;
4. the approved visual demo, but only as a design and workflow reference;
5. this plan;
6. approved Architecture Decision Records.

The mixed `Jober + CorvinumEU – Shared HR Operations Platform` document is **historical background only**. It must not introduce Corvinum requirements, multi-client abstractions, shift scheduling, fleet management, sick leave, Pohoda, or white-label product architecture into this build.

The earlier AI-completed questionnaire is not authoritative unless a specific answer is independently reconfirmed by Jober.

---

# 1. Coding-agent operating contract

The coding agent must:

1. Read this entire plan before changing code.
2. Inspect the existing demo and repository before implementation.
3. Preserve the approved Jober design language while migrating away from the demo's old frontend architecture.
4. Build for Jober only.
5. Never invent statuses, permissions, financial formulas, retention periods, blacklist rules, legal bases, or intake questions.
6. Store uncertain business values in configurable catalogs only when the structure is confirmed.
7. Mark temporary values as demo fixtures.
8. Prefer small, reviewable changes.
9. Add tests with every business-critical change.
10. Treat permissions, audit behavior, mobile usability, translations, and error handling as part of each feature.
11. Use fictional data until the real-data gate is satisfied.
12. Stop and produce a focused decision note when a missing decision would materially change workflow, data, security, or accounting results.
13. Do not build demand/order intake.
14. Do not build daily shifts, second shifts, bus rosters, vehicles, drivers, route planning, or capacity enforcement.
15. Do not build sick leave or vacation management.
16. Do not build worker accounts or a worker portal.
17. Do not build Pohoda integration, exploratory adapters, XML/mServer code, or placeholder abstractions.
18. Do not build payroll, invoicing, bank integrations, OCR, or a general document-management system.
19. Do not add React, Vite, a SPA framework, Node.js, npm, `package.json`, JavaScript lockfiles, or `node_modules`.
20. Use Playwright through Python and pytest.
21. Keep htmx, Alpine.js, and Tailwind pinned, local, checksum-verified, and documented.

When uncertain, expose the uncertainty. Do not fossilize a guess into a migration and then make humans excavate it.

---

# 2. Product vision

Build one private, multilingual Jober platform that replaces fragmented spreadsheets, memory, and phone-based administrative handoffs with a shared operational database and management-reporting layer.

The application contains two modules in one deployment and one PostgreSQL database:

## 2.1 Jober Workforce Operations

Supports:

- mandatory recruiter intake;
- candidate and worker records;
- duplicate and returning-person warnings;
- trial-day handoff and recycling;
- project assignment;
- automatic routing to project coordinators;
- four-pillar onboarding readiness;
- manager activation approval;
- accommodation and room occupancy;
- equipment, clothing, sizes, stock, valuation, and returns;
- entry medical and other approved compliance dates;
- weekly transport headcounts;
- exits, reassignment, and blacklist;
- worker feedback submitted through a public QR form;
- SMS communication;
- audit history and operational reports.

## 2.2 Jober Financial Oversight

Supports:

- manual monthly entry;
- project-level revenue and costs;
- accommodation-cost analysis;
- transport-cost analysis;
- whole-company totals;
- monthly and yearly profit/loss;
- locked historical periods and reproducible snapshots.

This is management oversight, not accounting software.

---

# 3. Business scale and operating constraints

Design for:

- approximately 600–700 active workers;
- approximately 20–30 new people per week;
- approximately 30–35 internal users;
- at least 5,000 historical person records;
- multiple Jober offices sharing one central company database;
- no office-level data isolation;
- mobile coordinator usage in the field;
- Hungarian, Slovak, and Ukrainian interfaces;
- broad operational read visibility across internal roles;
- action permissions enforced by role;
- private EU hosting;
- manual-first finance and transport reporting;
- strong auditability.

The system must favour correctness, traceability, mobile usability, and operational clarity over architectural novelty.

---

# 4. Confirmed product decisions

## 4.1 Removed from scope

The following are deliberately excluded:

- demand/order intake;
- factory-request screens;
- daily shift scheduling;
- multiple shifts per day;
- second-shift management;
- bus passenger rosters;
- vehicles and drivers;
- bus capacity enforcement;
- route planning;
- sick leave;
- vacation management;
- worker login/self-service;
- Pohoda;
- payroll calculation;
- invoice generation;
- bank integration;
- full document archive;
- OCR/AI extraction;
- general-purpose workflow builders;
- multi-client or white-label infrastructure;
- Corvinum-specific features.

## 4.2 Added or strengthened

The build must include:

- sequential hard-gated recruiter panels;
- typed negative answers for specified critical questions;
- one canonical five-value person lifecycle status;
- projects as the operational assignment unit;
- project-to-coordinator routing;
- trial handoff from recruiter to coordinator;
- fail/no-show recycling to the recruiter-visible available pool;
- manager approval blocked by four readiness pillars;
- accommodation pricing;
- equipment valuation and return checks;
- payroll-deduction candidate flags for missing returnable items, without performing payroll;
- weekly morning/noon/evening transport headcounts;
- worker feedback through a multilingual public QR form;
- manual financial oversight;
- entry-medical expiry alerts;
- SMS as the primary worker communication channel;
- broad internal read visibility with role-gated actions;
- mandatory old-value audit history.

---

# 5. Confirmed technology stack

## 5.1 Application platform

- Python.
- Django 6.x, pinned to a supported release at project initialization.
- PostgreSQL.
- Gunicorn.
- Django templates.
- Django forms and formsets.
- Django sessions.
- Django localization.
- Django management commands for scheduled jobs.
- Server-side authorization on every protected action.

Django owns routing, rendering, validation, authorization, workflow state, and persistence.

Do not create a general REST API for the browser. JSON endpoints require a demonstrated external integration need and an approved ADR.

## 5.2 Interaction and styling

- htmx, pinned and vendored locally.
- Alpine.js, pinned and vendored locally, used only for narrow local UI state.
- Tailwind CSS standalone CLI v4.3.0.
- Native browser APIs for trivial behaviour.
- No CDN-hosted runtime assets.

### htmx is appropriate for

- searches and filters;
- pagination;
- modal/drawer content;
- form submissions;
- inline validation;
- trial results;
- readiness updates;
- room assignment;
- inventory issue/return;
- status transitions;
- dashboard fragments.

### Alpine.js is limited to

- menu/drawer visibility;
- dropdowns;
- tabs;
- disclosure panels;
- modal visibility;
- ephemeral client-only selections.

Alpine must not own persisted data, permissions, business calculations, or workflow rules.

## 5.3 Tailwind build

The current Ubuntu 24.04 workstation has:

```text
/home/disane/.local/bin/tailwindcss
≈ tailwindcss v4.3.0
```

Development:

```bash
tailwindcss \
  -i static/src/css/app.css \
  -o static/dist/css/app.css \
  --watch
```

CI/production build:

```bash
tailwindcss \
  -i static/src/css/app.css \
  -o static/dist/css/app.css \
  --minify
```

Repository requirements:

- pin v4.3.0 until an explicit upgrade PR;
- add install/watch/build/version/checksum scripts;
- verify a checked-in SHA-256 manifest;
- permit `TAILWIND_BIN` override;
- never depend on the workstation installation in CI or Dokku;
- exclude the executable from the final runtime image;
- use no PostCSS, Sass, Vite, Node.js, or npm.

## 5.4 Browser testing

Use:

- `playwright` from PyPI;
- `pytest-playwright`;
- pytest fixtures/configuration;
- Playwright browser installation through Python;
- screenshots, traces, and video on failure.

Example:

```bash
python -m pip install playwright pytest-playwright
python -m playwright install --with-deps chromium
pytest tests/e2e
```

## 5.5 Deployment

- Dokku only.
- Docker-based build.
- Forpsi VPS for staging/demo and initial production.
- Dokku PostgreSQL service.
- Dokku reverse proxy and TLS.
- Git-based deployment.
- Separate staging and production apps.
- Multi-stage image: Tailwind in build stage, Python/Django in runtime.
- No Node.js or npm in the repository or production image.

## 5.6 Repository shape

```text
jober-platform/
├── manage.py
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   ├── offices/
│   ├── people/
│   ├── recruitment/
│   ├── projects/
│   ├── trials/
│   ├── onboarding/
│   ├── accommodation/
│   ├── inventory/
│   ├── compliance/
│   ├── transport_reporting/
│   ├── feedback/
│   ├── messaging/
│   ├── exits/
│   ├── blacklist/
│   ├── finance/
│   ├── reporting/
│   ├── imports/
│   ├── audit/
│   └── ui/
├── templates/
│   ├── layouts/
│   ├── components/
│   ├── fragments/
│   └── pages/
├── static/
│   ├── src/css/app.css
│   ├── dist/css/app.css
│   ├── src/js/app.js
│   └── vendor/
│       ├── htmx/htmx.min.js
│       └── alpine/alpine.min.js
├── locale/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── tools/
│   ├── install-tailwind.sh
│   ├── install-tailwind.ps1
│   ├── build-tailwind.sh
│   ├── watch-tailwind.sh
│   └── checksums/
├── infra/
├── docs/
│   ├── adr/
│   ├── product/
│   ├── data-model/
│   ├── permissions/
│   ├── dependencies/
│   └── runbooks/
└── .github/workflows/
```

---

# 6. Supply-chain rationale

The project intentionally uses one primary application ecosystem.

1. Django provides routing, templates, forms, validation, sessions, CSRF, authorization, localization, administration, and testing.
2. htmx and Alpine are small, pinned local assets.
3. Tailwind is one pinned standalone build executable.
4. Playwright runs through Python.
5. No production CDN is trusted for application assets.
6. No JavaScript package-manager dependency graph exists.
7. Python dependencies are locked and scanned.
8. Vendor files and binaries are checksum-verified.
9. The final image contains only runtime dependencies.

This is not risk elimination. It is risk reduction to a boundary humans can still comprehend before retirement age.

---

# 7. Existing demo reuse and correction plan

The demo remains the visual reference but not the architecture or complete workflow authority.

## 7.1 Preserve

- Jober branding;
- navigation concepts that still match confirmed workflows;
- dashboard composition where still relevant;
- page hierarchy;
- cards, badges, tables, panels, and spacing;
- mobile field-mode interaction ideas;
- approved terminology;
- useful Tailwind values and visual assets after provenance review.

## 7.2 Remove from the demo

- demand/order screen;
- daily shift assignment;
- second-shift screen;
- bus roster;
- vehicle capacity;
- sick-leave screen;
- worker portal;
- Pohoda concepts;
- any Corvinum/shared-client concepts;
- React/Vite/client-state architecture.

## 7.3 Add or substantially redesign

- hard-gated recruiter panels;
- project administration;
- project assignment;
- project-to-coordinator routing;
- trial handoff and recycling;
- four-pillar readiness;
- accommodation rates;
- inventory valuation and return checks;
- weekly transport headcounts;
- worker-feedback inbox;
- financial module;
- Ukrainian interface;
- entry-medical alerts.

## 7.4 Required migration documents

Create:

- `docs/product/source-register.md`;
- `docs/product/demo-inventory.md`;
- `docs/product/demo-to-django-map.md`;
- `docs/product/removed-demo-features.md`;
- `docs/product/open-decisions.md`.

The source register must explicitly mark the mixed Jober/Corvinum architecture as historical and non-authoritative.

---

# 8. Roles, visibility, and authorization

Use four fixed roles:

- Recruiter;
- Coordinator;
- Manager/Administrator;
- Observer.

Do not implement per-user permission matrices in the MVP.

## 8.1 Visibility principle

Jober's confirmed preference is broad internal read visibility:

- internal roles may view ordinary operational records across all offices;
- offices are filters and reporting fields, not access boundaries;
- roles restrict which actions may be performed;
- every sensitive change is audited.

Privacy and legal exceptions still apply:

- full sensitive identifiers must be masked/restricted;
- blacklist reasons are Manager/Admin only;
- feedback submissions are Manager/Admin only;
- security secrets and internal audit internals are restricted;
- exports are permission-controlled.

"Everyone can see everything" is an operational preference, not permission to ignore GDPR with theatrical confidence.

## 8.2 Recruiter actions

Can:

- create and edit intake during recruiter ownership;
- complete mandatory panels;
- search and view ordinary operational person data;
- assign a candidate to a project trial day;
- see trial results;
- see people returned to Available;
- recycle an Available person into another project;
- initiate approved SMS messages;
- see that a blacklist warning exists without seeing restricted reasons.

Cannot:

- record coordinator trial outcomes;
- complete operational readiness;
- approve Working status;
- manage projects, rooms, stock catalogs, users, finance, or blacklist decisions;
- view management-only worker feedback;
- erase audit history.

## 8.3 Coordinator actions

Can:

- view ordinary operational records;
- receive trial cards routed by project;
- mark pass, fail, or no-show in mobile field mode;
- complete medical/gear/accommodation/transport readiness data where assigned;
- assign rooms;
- issue and return equipment;
- record weekly transport headcounts;
- complete exit reconciliation;
- return eligible people to Available;
- initiate approved SMS messages.

Cannot:

- approve final Working status;
- change financial periods or formulas;
- manage users;
- decide blacklist cases;
- view restricted blacklist reasons or worker-feedback inbox;
- erase history.

## 8.4 Manager/Administrator actions

Can:

- perform all permitted operational reads;
- create/archive projects and set responsible coordinators;
- create/archive accommodations and rooms;
- manage catalogs;
- approve or reject activation;
- manage users and invitations;
- intervene in workflows with reasons;
- manage blacklist cases;
- view worker feedback;
- manage SMS templates/audiences;
- enter and lock financial periods;
- export approved data;
- view audit history.

## 8.5 Observer actions

Can:

- read approved operational dashboards and lists;
- read approved financial summaries;
- export only where explicitly allowed.

Cannot perform operational or financial writes.

## 8.6 Permission deliverable

Create `docs/permissions/permission-matrix.md` listing:

- every page;
- every command/action;
- sensitive fields;
- export permissions;
- feedback access;
- audit access;
- role result.

Every protected view and domain service requires direct authorization tests. A hidden button remains just a shy security bug.

---

# 9. Canonical lifecycle and ownership model

## 9.1 Person lifecycle status

Use one canonical person lifecycle status:

- `AVAILABLE`;
- `TRIAL_DAY`;
- `WORKING`;
- `INACTIVE`;
- `BLACKLISTED`.

Meaning:

### Available

Waiting for work or reassignment. May already have accommodation. Visible to recruiters for recycling.

### Trial Day

Assigned to a trial workflow and owned operationally by the project's coordinator.

### Working

Manager-approved and actively assigned to a project.

### Inactive

Not currently available but not blacklisted. Exact allowed reasons must come from a configured catalog.

### Blacklisted

Blocked across all Jober offices. Requires restricted manager review.

Do not restore the older dual hire-status/availability-status model unless Jober explicitly reverses the latest decision.

## 9.2 Workflow state belongs to workflow records

Draft intake, completed intake, trial outcome, readiness progress, approval decision, room assignment, and exit are stored on their relevant records.

Do not overload the five-value lifecycle status with every intermediate screen state.

## 9.3 Ownership transfer

- recruiter owns intake;
- recruiter schedules a project trial;
- the trial card leaves the recruiter's active queue;
- the project's coordinator receives it;
- fail/no-show returns the person to Available and the recruiter pool;
- pass keeps operational ownership with the coordinator;
- manager approval moves the person to Working;
- project assignment determines responsible coordinator.

All transfers are timestamped and audited.

---

# 10. Information architecture

## 10.1 Public/authentication routes

```text
/login
/password-reset
/invitations/<token>
/feedback/<public-token>
/health
```

The feedback route is the only worker-facing MVP interface and does not create a worker account.

## 10.2 Application routes

```text
/dashboard
/people
/people/new
/people/<uuid>
/people/<uuid>/history
/available
/trials
/trials/<uuid>
/readiness
/approvals
/projects
/projects/<uuid>
/accommodations
/accommodations/<uuid>
/inventory
/compliance
/transport-weekly
/messages/workers
/messaging
/exits
/blacklist
/finance
/finance/<year>/<month>
/reports
/audit
```

## 10.3 Management routes

```text
/management/users
/management/offices
/management/intake
/management/projects
/management/accommodations
/management/inventory
/management/compliance
/management/financial-categories
/management/sms-templates
/management/imports
```

Use `/management/`, not `/admin/`, for the branded client interface. Django Admin may exist only as a restricted support tool.

---

# 11. Core data model

Use UUID primary keys for externally referenced business records.

Important records include:

- `created_at`;
- `updated_at`;
- `created_by`;
- `updated_by`;
- lifecycle/active state;
- version/concurrency value where needed.

## 11.1 Accounts and offices

### User

- email;
- name;
- fixed role;
- preferred language;
- active state;
- invitation state;
- optional home office.

### Office

- name;
- code;
- active state.

Office never gates visibility in the MVP.

## 11.2 Person

### Person

- name fields;
- date/place of birth;
- phone;
- address;
- nationality/citizenship where approved;
- preferred language where approved;
- lifecycle status;
- current project assignment relation;
- responsible coordinator derived from project;
- rehire eligibility;
- archive metadata;
- search-normalized fields.

### PersonIdentifier

- person;
- identifier type;
- encrypted value where approved;
- masked display value;
- HMAC matching token;
- key version;
- verification metadata;
- retention metadata.

Raw identifier access is restricted and audited.

### WorkerProfile

Operational fields such as:

- clothing sizes;
- shoe size;
- accommodation preference;
- transport requirement;
- approved additional worker attributes.

The final field list must be supplied by Jober.

### PersonNote

- category;
- text;
- visibility classification;
- author;
- timestamp;
- revision trail.

## 11.3 Recruiter intake

### IntakeQuestionnaireVersion

- name/version;
- draft/published/retired;
- effective date;
- created by.

### IntakePanel

- questionnaire version;
- translated title/help;
- order;
- progression rule.

### IntakeQuestion

- panel;
- stable key;
- translated label;
- type;
- required flag;
- order;
- options;
- validation settings;
- `requires_typed_negative`;
- accepted normalized negative answers per language where approved;
- conditional rules.

### RecruitmentIntake

- person;
- recruiter;
- questionnaire version;
- current panel;
- draft/completed;
- started/completed timestamps.

### IntakeAnswer

- intake;
- question;
- typed/selected value;
- normalized value;
- answered by;
- timestamp.

Confirmed initial subjects include:

- identity;
- address;
- date of birth;
- invalidity/disability yes/no;
- invalidity/disability type where applicable;
- smoking;
- accommodation requirement;
- children;
- tax bonus monthly/yearly;
- payment to bank versus other;
- other approved Jober questions.

For critical negative answers, the recruiter must type the approved equivalent of "no/none"; a passive checkbox is insufficient.

The phrase "type + document" for disability requires clarification: whether Jober means metadata, an evidence-present flag, or a restricted file upload. Do not build a general document archive to guess the answer.

## 11.4 Projects and assignments

### Project

- name;
- partner;
- code;
- office;
- active state;
- responsible coordinator(s);
- notes;
- financial-reporting eligibility.

### ProjectAssignment

- person;
- project;
- start date;
- end date;
- status;
- assigned by;
- assignment reason;
- coordinator snapshot;
- audit metadata.

Only one current Working project assignment is allowed (Jober confirmed, round 4: a worker is on exactly one project at a time; history is retained). A `Project` may have several responsible coordinators (e.g. DHL BA has three), and a coordinator may run several projects — project↔coordinator is many-to-many.

Project assignment is the operational unit. There is no daily shift table.

## 11.5 Trials

### TrialAssignment

- person;
- project;
- coordinator derived from project;
- scheduled date/time;
- state: scheduled/completed/cancelled;
- outcome: pending/pass/fail/no_show;
- note;
- assigned by;
- outcome recorded by/at.

Trial history is append-preserving. A new attempt creates a new record.

## 11.6 Readiness and approval

### ReadinessRecord

- person;
- project;
- medical state;
- gear state;
- accommodation state;
- transport state;
- submitted by/at;
- readiness version.

Each pillar supports:

- incomplete;
- complete;
- not applicable, with explicit reason and actor.

### ActivationApproval

- readiness record;
- pending/approved/rejected;
- checklist snapshot;
- decision reason;
- decided by/at.

The manager approval button remains disabled until all four pillars are complete or explicitly not applicable.

Pillars (Jober confirmed, round 4):

1. medical — **always required**;
2. gear — **always required**;
3. accommodation — **may be N/A** (some workers are not housed / commute privately);
4. transport — **may be N/A** (private commute).

Accommodation and transport each carry an explicit "not applicable / private" state so the gate does not block a worker who legitimately needs neither. Medical and gear cannot be marked N/A.

**CARGO exception (round 4):** CARGO is a single, manager-run project with no onboarding ("just record that they're active"). The Manager may set such a person to Working via an **audited override** that bypasses the four-pillar gate. Model this as a manager override on the person (audited), not as a separate project type.

Approval moves the person to Working and creates/activates ProjectAssignment atomically.

## 11.7 Accommodation

### Accommodation

- name;
- address;
- active state;
- notes.

### Room

- accommodation;
- identifier;
- bed capacity;
- monthly rate;
- currency;
- active state;
- notes.

### AccommodationAssignment

- person;
- room;
- start/end;
- assignment-specific rate override if Jober needs exceptions;
- assigned/closed by;
- reason/note.

Rules:

- one active room per person;
- capacity enforced transactionally;
- moves close old assignment and create new;
- history preserved;
- occupancy/free beds reported;
- housing cost feeds financial reporting.

## 11.8 Inventory and equipment

### InventoryItemType

- name;
- category;
- size variant;
- unit;
- latest purchase price;
- currency;
- return-required flag;
- active state.

### StockMovement

- item;
- movement type;
- quantity;
- unit-price snapshot;
- timestamp;
- actor;
- reason.

### WorkerItemIssue

- person;
- item;
- quantity;
- issued by/at;
- return state;
- returned by/at;
- condition/note if later approved;
- missing/damaged amount;
- deduction-candidate flag;
- deduction-review state.

Rules:

- no serial-number tracking in MVP;
- stock cannot silently go negative;
- return-required chip cards/keys appear in exit reconciliation;
- missing items can create a deduction candidate;
- the platform does not execute payroll deductions.

Valuation uses the **latest purchase price**, priced **at the order date** so prior orders keep the price they were booked at (Jober confirmed, round 4; price entered manually per order, ~4–5 orders/year). Weighted-average is **not** used — this question is closed.

## 11.9 Compliance

### ComplianceType

- translated name;
- active state;
- warning interval;
- default validity metadata;
- readiness-pillar relation;
- manager verification requirement.

### ComplianceRecord

- person;
- type;
- issue/completion date;
- expiry date;
- status;
- entered by;
- verified by/at;
- note.

MVP stores dates/status only, not certificate scans.

### EntryMedicalRecord

May be implemented as a configured ComplianceType, but must support:

- one-year and two-year validity;
- alerts around month 11 or month 23;
- explicit expiry date;
- medical readiness relation.

No sick-leave model is created.

## 11.10 Weekly transport reporting

### WeeklyTransportHeadcount

- week start date, normalized to Monday;
- office;
- optional project if Jober confirms project-level entry;
- coordinator;
- morning count;
- noon count;
- evening count;
- note;
- entered/updated timestamps.

This records numbers only.

Do not create:

- worker-to-bus assignments;
- passenger manifests;
- vehicles;
- drivers;
- capacities;
- routes;
- daily shifts.

The exact reporting scope, office-only versus project-specific, remains an open Jober decision.

## 11.11 Feedback

### FeedbackPublicToken

- active/revoked;
- purpose;
- optional expiry;
- QR rendering reference.

### WorkerFeedbackSubmission

- language;
- anonymous/identified choice;
- optional person/contact identity;
- category;
- message;
- submitted timestamp;
- source metadata minimized for privacy;
- reviewed state;
- reviewed by/at;
- management note;
- retention metadata.

Rules:

- public multilingual form;
- one-way submission;
- no conversation thread;
- anonymous submission must remain genuinely anonymous within the declared policy;
- inbox visible only to Manager/Admin;
- rate limiting, honeypot/Turnstile decision, abuse controls, and privacy notice required;
- do not expose the internal person directory on the public form.

## 11.12 Messaging

### MessageTemplate

- name;
- channel;
- language;
- body;
- active state.

### MessageCampaign

- template;
- audience definition;
- created/approved/sent by;
- state;
- counts;
- timestamps.

### MessageDelivery

- campaign;
- person;
- destination;
- provider ID;
- delivery state;
- error category;
- timestamps.

SMS is the primary channel. Provider selection and exact MVP send volume remain open, but the domain model and provider adapter must not depend on Pohoda.

## 11.13 Exit and reassignment

### ExitRecord

- person;
- project;
- exit date;
- reason category;
- note;
- accommodation reconciliation;
- equipment reconciliation;
- return eligibility;
- resulting lifecycle status;
- recorded by.

Exit can result in:

- Available;
- Inactive;
- Blacklisted proposal.

## 11.14 Blacklist and matching

### BlacklistCase

- person;
- proposed/approved/rejected/removed;
- category;
- restricted reason;
- proposed by;
- decided by/at;
- review/expiry metadata.

### MatchFingerprint

- person or legally approved historical record;
- identifier type;
- HMAC;
- key version;
- active/revoked;
- retention metadata.

Rules:

- company-wide across offices;
- warning, not silent merge;
- recruiter sees warning state only;
- Manager/Admin reviews details;
- legal basis and retention must be approved before production execution.

## 11.15 Financial oversight

### FinancialCategory

- name;
- revenue/cost;
- reporting group;
- active state;
- order.

Expected groups include:

- wages;
- taxes/contributions;
- transport;
- accommodation;
- invoice revenue;
- medical;
- equipment/clothing;
- other approved costs.

### FinancialPeriod

- year/month;
- open/reviewed/locked;
- opened/locked by;
- timestamps.

### ProjectFinancialEntry

- period;
- project;
- category;
- decimal amount;
- currency;
- note;
- entered/updated by.

### AccommodationFinancialAllocation

Use operational accommodation rates where approved, with manual adjustment support and audit.

### TransportFinancialEntry

Manual transport amount by period and approved grouping.

### FinancialSnapshot

- locked input snapshot;
- category/formula version;
- project results;
- accommodation result;
- transport result;
- company result;
- created by/at.

Do not invent formulas. Jober's spreadsheet is required before production calculations are considered authoritative.

## 11.16 Imports and audit

### ImportJob / ImportRowResult

Support controlled Excel migration with preview, mapping, validation, duplicate review, confirmation, and row errors.

### AuditEvent

Append-only event containing:

- actor;
- action;
- entity;
- entity ID;
- timestamp;
- old values;
- new values;
- reason;
- request/correlation metadata;
- sensitive-value redaction.

---

# 12. Required workflows

## 12.1 Hard-gated recruiter intake

1. Recruiter starts intake.
2. Duplicate/match warning runs on approved identifiers.
3. Sequential panels are shown.
4. Every required answer must be present before continuing.
5. Critical negative answers require typed text matching the approved localized value.
6. Conditional details are required when the answer is positive.
7. Progress is saved server-side.
8. Completion creates or updates the permanent person record.
9. Person is Available unless blocked by a pending blacklist review.
10. Audit records the intake version and answers.

Acceptance:

- panels cannot be bypassed by URL or forged POST;
- server validation is authoritative;
- typed-negative normalization is tested per language;
- answers retain values after errors;
- recruiter ownership and timestamps are clear.

## 12.2 Trial handoff

1. Recruiter selects an Available person and project.
2. System derives the project's coordinator.
3. Trial assignment is created.
4. Person becomes Trial Day.
5. Card leaves recruiter's active queue.
6. Card appears in coordinator field mode.
7. Ownership transfer is audited.

## 12.3 Trial fail/no-show recycling

1. Coordinator marks fail or no-show.
2. Note/reason may be recorded.
3. Trial remains in history.
4. Person becomes Available.
5. Person reappears in recruiter pool.
6. Another trial may be scheduled without overwriting the first.

## 12.4 Trial pass and four-pillar readiness

1. Coordinator marks pass.
2. Person remains in coordinator-owned readiness workflow.
3. Medical, gear, accommodation, and transport pillars are completed.
4. Not-applicable requires explicit reason.
5. Manager approval remains disabled until all pillars resolve.
6. Coordinator submits readiness.
7. Manager approves or rejects with reason.
8. Approval atomically creates Working project assignment.
9. Rejection returns to readiness with an explicit state.

## 12.5 Project reassignment

1. Authorized user selects a new project.
2. System derives new coordinator.
3. Current assignment closes.
4. New assignment begins.
5. Ownership changes.
6. History and audit preserve both sides.

Exact rules for whether manager approval is required on every reassignment remain open.

## 12.6 Accommodation assignment/move

1. Coordinator selects person and room.
2. Capacity and active assignment are checked transactionally.
3. Rate is displayed.
4. Confirmation closes previous room and creates new assignment.
5. Occupancy/free beds update.
6. History remains visible.

## 12.7 Inventory issue/return and exit deduction candidate

1. Coordinator selects worker and item.
2. Stock and size are validated.
3. Issue and stock movement are atomic.
4. Return creates a return movement.
5. Missing return-required item creates a deduction candidate amount.
6. Manager can review the flag.
7. No payroll deduction is executed by this system.

## 12.8 Entry-medical alert

1. Date/expiry is recorded.
2. Scheduled command calculates warning state.
3. Dashboard shows upcoming/expired records.
4. Coordinator/Manager can navigate to the person.
5. Medical readiness blocks approval when required.

## 12.9 Weekly transport headcount

1. Coordinator opens current Monday-based week.
2. Enters morning/noon/evening counts.
3. Server validates non-negative integers.
4. Update is audited.
5. Trend report compares periods.
6. No person, bus, vehicle, or route record is created.

## 12.10 Worker feedback

1. Worker scans QR code.
2. Chooses HU/SK/UA.
3. Chooses anonymous or identified.
4. Selects category and enters message.
5. Privacy/abuse validation runs.
6. Submission appears in Manager/Admin inbox.
7. Manager marks reviewed and may add internal note.
8. No reply thread or worker account is created.

## 12.11 SMS campaign

1. Authorized user chooses template/language.
2. Defines approved audience.
3. System previews recipient count and exclusions.
4. User confirms.
5. Deliveries are queued/sent through provider adapter.
6. Results are logged.
7. Failed deliveries are visible without leaking sensitive content into logs.

## 12.12 Exit and recycling

1. Coordinator starts exit.
2. Open room and return-required items are shown.
3. Equipment/accommodation are reconciled.
4. Exit reason and return eligibility are recorded.
5. Result is Available, Inactive, or blacklist proposal.
6. Available people return to recruiter pool.

## 12.13 Blacklist warning

1. Intake matching detects a potential match.
2. Normal workflow is hard-gated.
3. Recruiter sees a restricted warning.
4. Manager reviews details.
5. Manager approves continuation or blacklist handling.
6. Decision is audited.
7. No automatic merge occurs.

## 12.14 Financial month

1. Manager opens period.
2. Enters project line items.
3. Accommodation and transport values are reviewed.
4. Decimal validation runs.
5. Monthly project and company results recalculate.
6. Manager locks period.
7. Immutable snapshot is created.
8. Reopen requires reason and audit.

## 12.15 Initial Excel import

1. Manager uploads Jober Excel.
2. System previews columns.
3. Mapping is confirmed.
4. Validation-only pass runs.
5. Duplicates and errors are reviewed.
6. Confirmed import executes safely.
7. Summary and audit are stored.
8. Repeated import cannot create uncontrolled duplicates.

---

# 13. Design system, mobile, and accessibility

## 13.1 Mobile-first viewports

Test:

- 360 × 800;
- 390 × 844;
- 768 × 1024;
- 1440 × 900.

Coordinator-critical screens must:

- avoid required horizontal scrolling;
- use approximately 44 × 44 CSS-pixel touch targets;
- expose one obvious primary action;
- use sticky mobile action bars where helpful;
- transform desktop tables into mobile cards/prioritized rows;
- avoid hover-only actions;
- preserve form values after errors;
- display htmx progress and recovery states;
- work while the on-screen keyboard is open;
- handle long HU/SK/UA labels without clipping.

Tailwind handles layout and breakpoints. Alpine handles local state. htmx handles server-backed updates. Django owns truth.

## 13.2 Reusable components

Create Django template components for:

- buttons;
- inputs;
- selects;
- dates;
- radio/checkbox groups;
- form errors and summaries;
- dialogs;
- tables/cards;
- pagination;
- filters/search;
- badges;
- alerts;
- drawers;
- tabs;
- timelines;
- empty states;
- request indicators;
- permission states;
- sticky mobile actions.

## 13.3 Accessibility

Require:

- keyboard navigation;
- visible focus;
- semantic controls;
- error summary and field errors;
- adequate contrast;
- no colour-only meaning;
- focus management for dialogs;
- live-region announcements for important htmx updates;
- localized accessible names.

## 13.4 Real-device gate

Before pilot:

- main coordinator flows tested on a real Android device;
- main flows tested on iPhone/Safari;
- slow-network simulation;
- public feedback form tested without authentication;
- SMS link/QR paths tested on phones.

---

# 14. Internationalization and Unicode

Client interface languages:

- Hungarian (`hu`);
- Slovak (`sk`);
- Ukrainian (`uk`).

English is not part of the initial client UI.

Requirements:

- no hard-coded visible strings;
- Django gettext catalogs;
- translated validation/permission text;
- localized dates, numbers, and currency;
- user language stored in profile/session;
- public feedback language selection;
- Unicode names and data across scripts;
- search normalization must not corrupt Cyrillic or other Unicode input;
- business names/projects are not machine-translated;
- approved terminology glossary.

---

# 15. Search, dashboards, and reports

## 15.1 Person search/filter

Support approved fields:

- name;
- phone;
- date of birth;
- lifecycle status;
- project;
- coordinator;
- office;
- accommodation/room;
- medical/compliance state;
- blacklist warning.

Use PostgreSQL indexes and normalized search fields. Do not add Elasticsearch without measured need.

## 15.2 Operational dashboards/reports

- Available people;
- Trial Day queue;
- readiness awaiting completion;
- approvals awaiting manager;
- Working people by project;
- project/coordinator counts;
- accommodation occupancy/free beds;
- stock, issued items, and valuation;
- missing return-required items;
- medical expiry;
- weekly transport trends;
- exits/recycling;
- SMS delivery summary;
- feedback inbox counts;
- authorized blacklist activity.

## 15.3 Financial reports

- project result;
- accommodation result;
- transport result;
- whole-company result;
- month comparison;
- yearly summary;
- locked period history.

## 15.4 Exports

- role-controlled;
- sensitive values masked/omitted;
- export event audited;
- large exports may become background jobs later.

---

# 16. HTTP, Django view, form, and htmx rules

- GET renders pages/fragments.
- POST performs state changes.
- Never mutate on GET.
- Use Django forms or explicit command forms.
- Use POST/Redirect/GET for full-page fallback.
- htmx and full-page requests share forms/services.
- Add `Vary: HX-Request` where needed.
- CSRF on every unsafe internal/public form as applicable.
- Public feedback receives abuse protection and rate limiting.
- Domain actions call service functions inside transactions.
- Use explicit commands, not generic CRUD, for:
  - trial outcome;
  - readiness submission;
  - approval;
  - room move;
  - stock issue/return;
  - project reassignment;
  - lifecycle transition;
  - blacklist decision;
  - financial lock/reopen;
  - import confirmation.
- Use `Decimal` for money.
- Use version checks on high-risk edits.
- Prevent double submission/idempotency issues.
- Unexpected errors expose a correlation ID, not internal details.

---

# 17. Notifications and scheduled work

## 17.1 Email

Used for:

- invitations;
- password reset;
- security notices;
- optional internal notifications.

## 17.2 SMS

SMS is a core Jober worker channel for approved operational broadcasts such as:

- pay dates;
- bus/transport changes;
- trial reminders;
- other approved notices.

Provider selection, sender identity, Slovak/Hungarian delivery constraints, and pricing must be decided before live sending.

## 17.3 Scheduled commands

Initial scheduled tasks:

- entry-medical/compliance warning recalculation;
- notification generation;
- backup-verification alert;
- retention review report only after legal approval;
- health/maintenance checks.

Commands must be idempotent and audited/logged.

Redis/worker queues are added only when committed volume requires them.

---

# 18. Security, privacy, and audit

## 18.1 Sessions

- HttpOnly;
- Secure in deployed environments;
- suitable SameSite;
- expiration;
- login rate limiting;
- CSRF;
- invitation/reset expiry;
- manager/admin 2FA before production unless product owner explicitly accepts another control.

## 18.2 Application security

- allow-list form validation;
- output escaping;
- security headers;
- CSP introduced carefully;
- no secrets in Git;
- no sensitive values in logs;
- Python dependency locking/scanning;
- vendored-asset checksum verification;
- public feedback abuse controls;
- export/download authorization;
- file size/type validation if any restricted attachment is approved.

## 18.3 Audit coverage

Audit at least:

- intake completion and critical answers;
- person/identifier changes;
- lifecycle transitions;
- ownership handoffs;
- project assignment;
- trial outcomes;
- readiness changes;
- approvals/rejections;
- accommodation moves/rates;
- stock movements and deduction candidates;
- compliance edits;
- weekly transport numbers;
- SMS campaigns;
- feedback review actions;
- exit/reassignment;
- blacklist activity and restricted views;
- finance edits/locks/reopens;
- users/roles;
- imports/exports.

Audit stores old and new values with appropriate redaction.

## 18.4 Retention and real-data gate

No automatic deletion/anonymization or production blacklist matching until written legal/retention rules are approved.

No real worker data until:

- DPA or equivalent is signed;
- hosting/security is approved;
- roles and sensitive-field visibility are reviewed;
- blacklist legal basis/retention is documented;
- feedback privacy notice/retention is documented;
- backups are configured and restored successfully;
- production security review passes.

---

# 19. File and attachment strategy

The MVP does not include a general document archive.

Confirmed compliance records are metadata/date based.

Before implementing any disability/supporting-document upload, Jober must clarify:

- whether a file must be retained;
- allowed types;
- legal basis;
- visibility;
- retention;
- encryption;
- malware scanning;
- backup.

If approved, use protected storage with authorization checks and metadata in PostgreSQL. Never expose permanent public URLs.

---

# 20. Testing plan

## 20.1 Unit/integration

Test:

- lifecycle transitions;
- typed-negative validation;
- panel sequencing;
- duplicate/HMAC warnings;
- ownership transfer;
- project-to-coordinator routing;
- trial recycling;
- four-pillar hard gate;
- project assignment transactions;
- room capacity concurrency;
- stock concurrency and valuation snapshots;
- deduction-candidate rules;
- medical warnings;
- weekly headcount validation;
- public feedback anonymity/identification;
- feedback permissions;
- SMS audience selection;
- blacklist permissions;
- finance calculations/locking;
- imports;
- audit coverage.

## 20.2 Django/template/htmx

Test:

- role navigation;
- broad reads and action gates;
- full-page and htmx response variants;
- form values/errors;
- CSRF;
- fragment headers;
- translations;
- filters/pagination;
- mobile cards;
- dialogs;
- error/permission/conflict states;
- Alpine reinitialization after swaps.

## 20.3 Playwright end-to-end

Automate:

1. recruiter completes hard-gated intake;
2. critical typed-negative rule blocks passive omission;
3. recruiter assigns trial to project;
4. card routes to coordinator;
5. no-show returns person to Available;
6. second trial passes;
7. four pillars are completed;
8. manager cannot approve early;
9. manager approves and person becomes Working;
10. project reassignment changes coordinator;
11. room assigned/moved;
12. inventory issued/returned;
13. missing key creates deduction candidate;
14. medical warning appears;
15. weekly transport counts are entered and trended;
16. anonymous feedback reaches Manager but not Coordinator;
17. identified feedback works;
18. SMS preview and mocked delivery work;
19. exit returns eligible person to Available;
20. blacklist match gates workflow;
21. financial month is entered and locked;
22. Excel validation/import runs safely.

Run coordinator flows at desktop and mobile viewports.

## 20.4 Performance baseline

Seed/test:

- 5,000+ people;
- realistic trial/audit history;
- 30–35 users;
- search/filter load;
- accommodation occupancy;
- stock movements;
- finance yearly reports;
- feedback and messaging histories.

---

# 21. Infrastructure, backup, and monitoring

## 21.1 Environments

### Local

- documented Python/Django setup;
- PostgreSQL;
- fictional fixtures;
- local email capture;
- mocked SMS;
- repeatable commands;
- Tailwind watch.

### Staging

- Dokku;
- fictional/approved test data;
- protected access;
- production-like settings;
- automatic approved-branch deployment.

### Production

- separate Dokku app/database;
- real TLS/domain;
- restricted admin access;
- encrypted secrets;
- backups;
- monitoring;
- DPA gate.

## 21.2 Backup scope

Back up:

- PostgreSQL;
- approved protected files;
- encryption/HMAC keys through a separate secure procedure;
- deployment/runbook/config documentation.

## 21.3 Backup requirements

- daily automated database backup;
- encrypted off-site copy;
- retention policy;
- failure alert;
- periodic restore test;
- written restore runbook.

## 21.4 Monitoring

Monitor:

- uptime/health;
- HTTP errors;
- CPU/memory/disk;
- database availability/growth;
- failed scheduled jobs;
- backup success;
- container restarts;
- login abuse;
- public feedback abuse signals;
- SMS delivery failures.

Gotify may receive alerts. It is not the monitoring engine.

---

# 22. CI/CD rules

CI must run:

- Python formatting/linting;
- type checking if adopted;
- Django checks;
- migration consistency;
- unit/integration/view/template tests;
- Tailwind v4.3.0 compilation and checksum verification;
- htmx/Alpine checksum verification;
- Playwright Python smoke/E2E tests;
- dependency vulnerability scan;
- secret scan;
- production Docker build;
- assertion that repository/image contain no Node.js/npm artifacts.

Deployment:

- only after CI;
- documented migration release step;
- Tailwind build then `collectstatic`;
- health check;
- rollback procedure;
- database backup before risky releases.

---

# 23. Implementation phases

## Phase 0: Source reconciliation and demo migration

Deliver:

- source register;
- open-decision register;
- demo inventory;
- removed-feature inventory;
- demo-to-Django map;
- repository skeleton;
- local environment;
- Dokku staging shell;
- vendored htmx/Alpine;
- Tailwind v4.3.0 build;
- base template/design tokens;
- one mobile htmx interaction.

Exit:

- Corvinum/shared assumptions marked non-authoritative;
- removed demo screens identified;
- app works locally/staging;
- no npm/React/Vite;
- architecture ADRs approved.

## Phase 1: Real vertical workflow

Build:

- auth/roles/languages/audit;
- project administration;
- hard-gated intake;
- Person and lifecycle status;
- trial handoff;
- fail/no-show recycling;
- four-pillar readiness;
- manager approval;
- minimal room assignment;
- minimal inventory issue;
- entry-medical date;
- weekly transport entry;
- minimal financial month;
- fictional seed/reset.

Exit:

One fictional person moves through intake → trial failure → Available → second trial → readiness → manager approval → Working project assignment using real Django/PostgreSQL.

## Phase 2: Workforce operations core

Build:

- full person card/history/search;
- all intake panels;
- project/coordinator routing;
- complete trials;
- full readiness;
- dashboards;
- approved SMS messaging;
- exports.

## Phase 3: Logistics, feedback, exit, blacklist

Build:

- accommodation pricing/occupancy;
- inventory valuation/returns;
- compliance alerts;
- transport trends;
- QR feedback/inbox;
- exits/recycling;
- blacklist/HMAC review;
- operational reports.

## Phase 4: Financial oversight

Build after Jober supplies formulas:

- categories;
- monthly entry;
- project/accommodation/transport/company results;
- lock/snapshot/reopen;
- yearly reports.

## Phase 5: Import and production pilot

- Excel importer;
- legal/privacy sign-offs;
- security review;
- performance test;
- backup restore;
- monitoring;
- training;
- controlled pilot;
- acceptance.

---

# 24. Coding work packages

## Foundation

- **WP-00:** Source register and authority matrix.
- **WP-01:** Repository/local environment.
- **WP-02:** Demo inventory and removed-feature map.
- **WP-03:** Demo-to-Django migration map.
- **WP-04:** Django/htmx application shell.
- **WP-05:** Tailwind v4.3.0, vendored assets, template components.
- **WP-06:** Mobile-first layout primitives.
- **WP-07:** Dokku staging.

## Platform

- **WP-08:** Invitations/session authentication.
- **WP-09:** Four-role action authorization and broad-read policy.
- **WP-10:** HU/SK/UA localization.
- **WP-11:** Append-only audit infrastructure.
- **WP-12:** Standard forms/htmx/error/conflict conventions.

## People and intake

- **WP-13:** Person/identifier/worker profile.
- **WP-14:** Questionnaire versions/panels/questions.
- **WP-15:** Typed-negative validation.
- **WP-16:** Recruiter intake wizard.
- **WP-17:** Duplicate/blacklist warning service.
- **WP-18:** Person search/card/history.
- **WP-19:** Five-value lifecycle engine.

## Projects and trials

- **WP-20:** Project and coordinator administration.
- **WP-21:** Project assignment/history.
- **WP-22:** Trial assignment and ownership handoff.
- **WP-23:** Mobile pass/fail/no-show.
- **WP-24:** Available pool and recycling.

## Readiness and approval

- **WP-25:** Four-pillar readiness model.
- **WP-26:** Coordinator readiness UI.
- **WP-27:** Manager approval/rejection.
- **WP-28:** Entry medical/compliance.
- **WP-29:** Expiry scheduled command/dashboard.

## Accommodation and inventory

- **WP-30:** Accommodation/room/rates.
- **WP-31:** Atomic assignment/move/occupancy.
- **WP-32:** Inventory catalog/stock/latest price.
- **WP-33:** Worker sizes and item issue/return.
- **WP-34:** Exit deduction-candidate review.
- **WP-35:** Logistics reports.

## Transport, messaging, feedback

- **WP-36:** Weekly headcount entry.
- **WP-37:** Weekly trend reporting.
- **WP-38:** SMS templates/provider adapter/outbox.
- **WP-39:** SMS campaign preview/send/reporting.
- **WP-40:** QR/public feedback form.
- **WP-41:** Management feedback inbox.

## Exit and blacklist

- **WP-42:** Exit/reconciliation.
- **WP-43:** Rehire/Available routing.
- **WP-44:** Blacklist case workflow.
- **WP-45:** HMAC matching/restricted review.

## Finance and reporting

- **WP-46:** Role-aware dashboards.
- **WP-47:** Operational reports/exports.
- **WP-48:** Finance categories/periods.
- **WP-49:** Monthly entry.
- **WP-50:** Calculation/reporting.
- **WP-51:** Lock/reopen/snapshot.

## Import and production

- **WP-52:** Excel preview/mapping/validation/import.
- **WP-53:** Fictional seed/reset.
- **WP-54:** E2E suite.
- **WP-55:** Security/privacy verification.
- **WP-56:** Backup/restore/monitoring.
- **WP-57:** Production runbooks.
- **WP-58:** Pilot/training/acceptance.

---

# 25. Dependency order and parallelization

Required chain:

```text
Source reconciliation
→ Demo migration shell
→ Auth/roles/i18n/audit
→ Person/lifecycle/projects
→ Intake/trials
→ Readiness/approval
→ Accommodation/inventory/compliance
→ Transport/messaging/feedback
→ Exit/blacklist
→ Finance/import
→ Pilot
```

After shared contracts are merged, separate agents may work on:

- accommodation;
- inventory;
- compliance;
- weekly transport reporting;
- feedback;
- messaging;
- finance;
- reports;
- infrastructure.

They may not independently redefine:

- Person;
- lifecycle statuses;
- roles;
- Project/ProjectAssignment;
- audit schema;
- form/htmx conventions;
- design tokens;
- translation keys.

---

# 26. Definition of ready

A feature is ready when:

- Jober objective is stated;
- roles/actions are known;
- inputs are confirmed or explicitly configurable;
- transitions/exceptions are defined;
- visibility and sensitive-field rules are defined;
- audit behaviour is defined;
- mobile behaviour is defined;
- acceptance criteria exist;
- unresolved decisions are listed.

---

# 27. Definition of done

A work package is done only when:

- acceptance criteria pass;
- tests cover domain/view/form/template/browser behaviour;
- authorization is tested;
- audit is tested;
- migrations are reviewed;
- mobile and desktop states work;
- validation/error/empty/conflict/permission states exist;
- HU/SK/UA strings use localization;
- documentation is updated;
- production image builds without Node/npm;
- no critical/high issue remains;
- staging deployment succeeds;
- rollback implications are documented.

---

# 28. Required Jober inputs and open decisions

## Business inputs

**Resolved in round 4** (see `jober_answers_round4.md` and `finance_module_spec.md`; authoritative over older text):

- Recruiter panels approved; **typed "no" required only for invalidity and smoking**, the rest may be toggles (#1).
- **Project/coordinator mapping** provided (DHL BA → Mesík Samuel, Dimitrii Strelnikov, Alexander Kovalenko; DHL Gáň & DHL Nitra & MINIT & C2I → Tibor Bódis; WEBASTO & MEVIS → Dezider Póda; CARGO → manager). **Project↔coordinator is many-to-many** (#6).
- **One active project per worker** at a time (#8).
- **Four-pillar N/A rules:** medical + gear always required; accommodation + transport may be N/A (#10).
- **Equipment valuation:** latest purchase price at order date, manual entry; weighted-average not used (#13).
- **Compliance alert intervals:** 11 and 23 months (#15).
- **SMS:** no provider yet — SyncMetric selects provider/sender; volume ≥ ~400/month; **coordinators may send to their own project**; **arbitrary per-recipient selection required**; worker messages manually composed; **no Telegram bot** (Jober runs an existing manual Telegram broadcast channel) (#17 — see `messaging_specification.md`).
- **Feedback retention:** 1 month (#18).
- **Blacklist:** 5-year archive, **Manager-only removal** (legal basis still pending lawyer) (#20).
- **Applicant (never-hired) retention:** 5 years (relates to §18.4).
- **Employment classification:** Jober's own employees, **leased out** to client companies (munkaerő-kölcsönzés); mandatory-document and controller specifics pending lawyer.
- **Financial model:** line items, groups, and calculations reverse-engineered in `finance_module_spec.md` (#21).

**Still open:**

3. Meaning/storage requirement of disability "document".
4. Exact remaining fields on Person and WorkerProfile.
5. Allowed Inactive reasons.
7. Office spellings — Jober was unsure what's needed; **recommend dropping "office" as a concept** unless a concrete need surfaces (projects are the operational unit). Do not model speculatively.
9. Whether project reassignment needs manager approval.
11. Accommodation list, rooms, capacities, rates, overrides.
12. Inventory catalog, sizes, opening stock, purchase prices.
14. Deduction-candidate review process detail.
21/22. **Finance sign convention + one filled month** — the supplied Excel is the blank template; a filled month is needed to confirm whether costs are entered negative (`profit = costs + revenues`) or positive (`revenues − costs`). The active-worker data sample is also still outstanding.
23. Branding assets and approved terminology.
24. DPA and production approval (lawyer).

## Explicitly not open in this project

- Corvinum applicability;
- shared codebase/white-label strategy;
- shift scheduling;
- fleet management;
- sick leave;
- worker portal;
- Pohoda.

Those require separate projects or explicit future commercial scope.

---

# 29. Confirmed decision register

| Decision | Status | Consequence |
|---|---|---|
| Client scope | Confirmed | Jober only |
| Corvinum/shared architecture | Rejected for this build | Historical reference only |
| Existing demo | Confirmed visual baseline | Migrate design, remove obsolete workflows |
| Django | Confirmed | Full-stack framework |
| htmx | Confirmed | Vendored server interaction layer |
| Alpine.js | Limited | Local ephemeral UI only |
| Tailwind standalone v4.3.0 | Confirmed | npm-free CSS build |
| Playwright Python | Confirmed | Browser tests via pytest |
| React/Vite/Node/npm | Rejected | None in repository/build/runtime |
| PostgreSQL | Confirmed | System of record |
| Dokku | Confirmed | Deployment platform |
| Project assignment | Confirmed | Operational unit |
| Person↔project cardinality | Confirmed (r4) | One active project per worker; history retained |
| Project↔coordinator | Confirmed (r4) | Many-to-many; a project may have several coordinators |
| CARGO onboarding exception | Confirmed (r4) | Manager audited override to mark Working without the four-pillar gate |
| Daily shifts/bus rosters | Removed | No shift/vehicle/driver/capacity model |
| Lifecycle statuses | Confirmed | Available, Trial Day, Working, Inactive, Blacklisted |
| Broad internal reads | Confirmed | Actions restricted by role; sensitive exceptions remain |
| Audit old/new values | Confirmed | Safety control for shared visibility |
| Hard-gated recruiter panels | Confirmed | Sequential server-enforced intake; typed "no" for invalidity + smoking |
| Four readiness pillars | Confirmed (r4) | Medical + gear always; accommodation + transport may be N/A |
| Compliance alert intervals | Confirmed (r4) | 11 and 23 months |
| Worker feedback | Confirmed | Public QR form, anonymous/identified, Manager only; 1-month retention |
| Weekly transport counts | Confirmed | Manual morning/noon/evening totals |
| Accommodation pricing | Confirmed | Room rates feed oversight |
| Inventory valuation/returns | Confirmed (r4) | Latest purchase price at order date, manual entry; no weighted-average |
| SMS | Confirmed (r4) | SyncMetric picks provider/sender; coordinators send to own project; per-recipient selection; manual worker messages |
| Telegram | Confirmed (r4) | Existing manual broadcast channel; no bot, no per-worker model in scope |
| Financial oversight | Confirmed | Manual monthly project/accommodation/transport/company results; line items per `finance_module_spec.md` |
| Finance sign convention | Open | Confirm via one filled month before sign-off |
| Blacklist retention/removal | Confirmed (r4) | 5-year archive, Manager-only removal; legal basis pending lawyer |
| Applicant retention | Confirmed (r4) | 5 years |
| Employment classification | Confirmed (r4) | Own employees leased out (munkaerő-kölcsönzés); doc/controller specifics pending lawyer |
| Pohoda | Out of scope/deferred | No code or hidden adapter |
| Sick leave/vacation | Removed | No models/screens |
| Worker portal | Removed | Feedback form only |
| Languages | Confirmed | HU/SK/UA, no English UI |

---

# 30. First coding-agent assignment

## Objective

Complete Phase 0 without implementing broad business features.

## Tasks

1. Read this plan and the Jober v0.4 delta.
2. Create `docs/product/source-register.md`.
3. Mark the mixed Jober/Corvinum architecture historical/non-authoritative.
4. Inventory every demo route/component.
5. Identify and document screens to remove.
6. Produce `demo-to-django-map.md`.
7. Create Django modular-monolith skeleton.
8. Configure PostgreSQL.
9. Vendor htmx and Alpine with licenses/checksums.
10. Add Tailwind v4.3.0 install/watch/build/checksum scripts.
11. Recreate login, layout, navigation, and one corrected dashboard screen.
12. Implement one mobile htmx interaction with full-page fallback.
13. Add Python CI, Docker build, Dokku staging skeleton.
14. Add Playwright Python desktop/mobile smoke tests.
15. Add ADRs for:
    - Jober-only scope;
    - modular monolith;
    - Django server rendering;
    - htmx/Alpine constraints;
    - Tailwind standalone;
    - npm exclusion;
    - Playwright Python;
    - broad-read/action-gated RBAC;
    - demo reuse;
    - project assignment replacing shifts;
    - Pohoda exclusion.
16. Do not finalize person fields, typed-negative phrases, financial formulas, blacklist retention, or disability-document storage.

## Required output

- repository tree;
- local setup;
- source register;
- open-decision register;
- demo inventory;
- removed-feature inventory;
- demo-to-Django map;
- vendor manifest;
- ADRs;
- working local/staging shell;
- representative mobile interaction;
- Playwright smoke tests;
- risk/blocker list;
- recommended Phase 1 task.

## Acceptance

- Django connects to PostgreSQL;
- Tailwind v4.3.0 builds locally/CI;
- no Node/npm/React/Vite artifacts;
- htmx/Alpine served locally;
- corrected demo shell renders;
- obsolete shift/demand/sick/Pohoda/Corvinum navigation is absent;
- mobile and desktop smoke tests pass;
- health endpoint succeeds;
- no real PII;
- Dokku path documented/working.

---

# 31. Revision history

## v3.1 — Round-4 reconciliation

Folded in the manager's round-4 answers and the reverse-engineered finance model so there is a single contradiction-free source for the build:
- single active project per worker; project↔coordinator many-to-many; CARGO manager-override exception;
- four pillars split into always-required (medical, gear) vs may-be-N/A (accommodation, transport);
- equipment valuation closed (latest price at order date, manual; no weighted-average);
- compliance alerts 11/23 months; feedback retention 1 month; blacklist 5-year archive, Manager-only removal; applicant retention 5 years; employment = own employees leased out;
- SMS refinements (per-recipient selection, coordinator-scoped sending, no Telegram bot — existing manual channel);
- §28 open-inputs split into resolved vs still-open; §29 register updated; finance line items delegated to `finance_module_spec.md` (sign convention still to confirm from one filled month).

## v3.0 — Jober-only post-second-interview alignment

- Corvinum and white-label/shared-platform assumptions removed.
- Latest Jober interview delta promoted to top business authority.
- Shift, fleet, capacity, sick leave, worker portal, and demand intake removed.
- Project assignment made the operational unit.
- Five lifecycle statuses adopted.
- Recruiter hard-gates and typed negatives added.
- Trial handoff/recycling clarified.
- Four-pillar manager approval added.
- Accommodation rates and inventory valuation/return checks expanded.
- Weekly transport headcounts added.
- Public worker feedback added.
- SMS promoted to core communication.
- Financial module confirmed manual-first.
- npm-free Django/htmx/Tailwind/Playwright architecture retained.

---

# 32. Final instruction

Build dependable Jober infrastructure, not a speculative staffing-industry platform.

The first meaningful success is one fictional person moving through the confirmed Jober flow while permissions, ownership, mobile usability, old-value audit history, and financial/operational truth remain intact.

Do not make Corvinum, abandoned shifts, or uncooperative accounting software rise from the dead in a pull request.