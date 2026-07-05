> **Status: FUTURE-STAGE PLANNING — second-client requirements, not the Jober
> build.** Non-authoritative for the current single-client Jober app
> ([ADR 0001](../adr/0001-jober-only-scope.md)); the platform is extracted only
> after Jober is complete ([ADR 0020](../adr/0020-white-label-platform-sequencing.md)).
> This is the CorvinumEU v0.6-draft as supplied; it informs the shared-core
> extraction and the eventual CorvinumEU thin client only, and authorises no
> platform/Corvinum code in the current build.
>
> **Addendum 2026-07-05 (fuel-money tracking, secondhand — see end of file):**
> a new requirement relayed via the CorvinumEU secretary, recorded as **pending
> confirmation** through the interview channel. It does not modify the v0.6-draft
> body above; see "Addendum A1" after §16.

# CorvinumEU PeopleOps – HR Management Product Design

**Document type:** Working product design draft  
**Version:** v0.6-draft  
**Status:** Internal working document  
**Prepared for:** Syncmetric / CorvinumEU discovery and proposal planning  
**Language:** English working draft  

> **v0.4 reconciliation note.** This version is rewritten against the first CorvinumEU client interview, which **overturned two assumptions baked into v0.3**: transportation route/vehicle logistics and automated SMS/email notifications are **both rejected** for this client. Routes change constantly, drivers will not maintain them, and worker contact happens by phone call and Facebook Messenger. In their place the interview surfaced the real operational core: a **cash advance and deduction ledger** and **equipment/clothing issuance with cost recovery**. Equipment, previously excluded, is now **in scope**.
>
> **Open financial boundary.** The advance / deduction / travel-money cluster is, in effect, a lightweight per-worker cash ledger netted against pay. It sits on the edge of the original "no financials" rule, which was meant to exclude profit/loss and accounting integration. This document treats the per-worker ledger as **in scope (operational cash tracking)** but flags it for explicit client sign-off — see 13.1. Profitability dashboards, payroll, and accounting-system integration remain out.
>
> **Source.** Decisions below marked "(interview)" come from that first call; they are not assumed to match Jober.
>
> **v0.5.** Adds a design-language section (7.0) aligning the app to the existing **corvinum.eu** brand and the admin panel already embedded in that site. Stack confirmed as Django/htmx, derived from the Jober build (section 12).
>
> **v0.5.1 — architecture decision locked.** Syncmetric is building a **white-label staffing-agency HR platform**, not bespoke per-client systems. Jober and CorvinumEU are the first two clients of one shared codebase. **Fork and long-lived-branch options are rejected.** Build order: **finish Jober first → extract the shared core from it → build CorvinumEU as the first thin client** (features + theme + config). See 12.4 and the build roadmap in 12.5.
>
> **v0.5.2 — acceptance criteria corrected.** The platform-validation bar is no longer "zero changes to the core" (which would force client logic into the wrong places). It is now: no client-specific conditional logic in the core, core changes must be genuinely reusable, and Jober behavior preserved through tests. See 12.5 Stage D.
>
> **v0.5.3 — admin-component reuse gated by audit.** The corvinum.eu admin components (login, 2FA, applicant inbox, job CRUD) are treated as reuse *candidates*, not confirmed reuse. They require an audit (ownership, stack, auth compatibility, production quality, asset/licence reuse, supply-chain rules) before any are counted as done. Default is "reuse the design, re-implement in our stack." See 7.0.
>
> **v0.5.4 — no CDN runtime assets.** Material Symbols (and any other external font/icon/asset) must not be loaded from Google or any CDN at runtime. They are obtained via the asset-request process, recorded with source/licence/version/checksum, vendored locally, and served by the app. See 7.0 and 12.3.
>
> **v0.6-draft — ledger remodel + extraction boundaries.** The advance ledger moves from a single signed `amount` to explicit fields (`entry_type`, positive `amount`, `pay_effect`, `settlement_status`) so cash movement and payroll effect can no longer be conflated (5.10, data model). Ledger rules that must be fixed before build are listed (timezone/cutoff, cycle boundaries, correction vs deletion, reversal, partial recovery, immutability, export layout). Repo boundaries refined: documents, checklists, and duplicate/blacklist are **features**, not core; client layers carry explicit **policy/workflow interfaces** (12.4). This is a working draft toward an implementation-grade v0.6 — see the v0.6 checklist at the end of section 12.

---

## 1. Purpose of this document

This document turns the CorvinumEU HR/CRM questionnaire answers into a first product design for an internal HR management system.

The goal is not to design a generic CRM. The goal is to design a practical **HR operations platform** for managing candidates, workers, recruiters, coordinators, HR/admin users, observers, documents, approvals, assignments, equipment issuance, cash advances and deductions, and compliance-sensitive workflows.

This is a working document. It is intentionally structured so we can revise it section by section during the back-and-forth.

---

## 2. Product concept

### Working product name

**CorvinumEU PeopleOps**

### Product category

Internal HR operations and recruitment management system.

### Core promise

> Every candidate and worker has one reliable profile, one current status, one document state, one assignment history, and one controlled approval path.

### What the system should solve first

The first version should reduce operational confusion around:

- candidate and worker records;
- duplicated people in the system;
- blacklist and re-application detection;
- document expiry and missing-document risks;
- unclear status ownership;
- recruiter/coordinator handoff problems;
- cash advances tracked in Excel/paper with no reliable weekly summary or salary-deduction trail;
- issued clothing/equipment not tracked, so unreturned items are never recovered;
- manual operational tracking in Excel, paper, calls, and scattered messages;
- lack of reliable visibility for HR/admin users and management.

---

## 3. Explicit non-goals for CorvinumEU

These are intentionally excluded from the current CorvinumEU product scope.

### Out of scope for MVP

- economic / profit-and-loss dashboard;
- earnings/losses or project-profitability reporting;
- payroll automation;
- payroll/accounting software integration (e.g. Pohoda);
- accommodation, room, bed, lodging, or housing logistics;
- accommodation cost tracking, rooming lists, rent deductions;
- transportation route / vehicle / driver logistics (interview: explicitly rejected — routes change constantly and drivers will not maintain them);
- automated SMS / email notification sending (interview: rejected for MVP — worker contact is by phone call and Facebook Messenger);
- worker self-service or feedback portal;
- daily shift / rota tables for workers.

### In scope, confirmed by interview (v0.4)

- **Advance & deduction ledger** — per-worker cash advances against wages, deductions, and additions (travel/fuel), with explicit entry-type/pay-effect fields, weekly summary, 20th-to-20th cycle, and search — see module 5.10.
- **Equipment & issued items** — clothing, shoes, tools, medical items issued with recorded sizes and values, return tracking, and cost recovery (deduction) when not returned — see module 5.8.
- Intake details captured at candidate creation: children, smoking, drinking, invalidity, tax bonus.
- Payment method per person (cash vs. bank transfer).
- CV (résumé) stored, printable, and forwardable to the partner company.
- Blacklist for returning banned people (confirmed).

> **Financial boundary.** The ledger is operational cash tracking, not accounting. It records what was advanced/deducted per person and nets against pay; it does **not** do P&L, invoicing, or accounting export. This boundary needs client confirmation (13.1).

### Possible future scope, only if requested later

- automated SMS / messaging templates ("maybe later" per interview);
- payroll / accounting export;
- advanced BI dashboard;
- offline-capable PWA mode;
- AI-assisted document extraction.

---

## 4. Primary users and responsibilities

## 4.1 User roles

| Role | Main responsibility | Access level |
|---|---|---|
| Recruiter | Create and manage candidates before activation | Own candidates, limited document upload, duplicate warnings |
| Coordinator | Manage operational worker activity, equipment issuance, and field-level changes | Assigned workers/projects, quick notes, status updates, document status visibility, equipment issuance |
| HR Admin | Verify documents, approve profile completeness, manage HR process | Full worker/candidate HR data, document review, approvals |
| Regional / Operational Manager | Oversee recruiters/coordinators and approve sensitive decisions | Region/project-level visibility, activation approval, blacklist approval |
| System Admin | Manage users, permissions, settings, audit logs | Full system access |
| Observer / Read-only User | View selected reports and records without editing | Read-only access to permitted data |
| Owner / Executive | See high-level operational state | Management dashboard and reports |

## 4.2 Permission principles

The system should use role-based access control from the beginning.

Core rules:

- recruiters should not see all historical HR data by default;
- coordinators should see operationally necessary data, not every sensitive document;
- HR/admin users should verify documents and approve sensitive transitions;
- blacklist reasons should be restricted to HR/management/admin roles;
- advance and deduction entries are sensitive financial data, visible/editable only to office/HR/management roles, not to recruiters by default;
- equipment issuance and return can be recorded by coordinators/HR for their own workers;
- observers should not be able to modify records;
- all sensitive changes should be audit logged.

---

## 5. Core product modules

## 5.1 People Registry

The central database for every person in the system.

### Person types

- candidate;
- tested candidate;
- pending worker;
- active worker;
- archived worker;
- blacklisted person.

### Required capabilities

- create person record;
- edit person record;
- view current status;
- view assignment history;
- view document status;
- view activity timeline;
- search by name, phone, email, birth date, ID/passport, status, project, recruiter, coordinator;
- detect possible duplicates during creation;
- prevent uncontrolled duplicate creation.

### Recommended profile tabs

- Overview;
- Personal data;
- Contact data;
- Identifiers;
- Status history;
- Documents;
- Assignments;
- Equipment / issued items;
- Advances / deductions;
- Checklist / approvals;
- Notes / activity timeline;
- Duplicate / blacklist warnings;
- Audit trail, admin-only.

---

## 5.2 Recruitment Pipeline

This module manages the process from first contact to activation.

### Suggested stages

1. New lead / interested person
2. Candidate
3. Screened / interviewed
4. Test scheduled
5. Tested candidate
6. Pending documents / pending approval
7. Active worker
8. Archived
9. Blacklisted

### Recruiter responsibilities

- create new candidate;
- record source/channel;
- collect basic data;
- upload initial documents when available;
- schedule interview/test;
- record screening result;
- hand off to coordinator/HR;
- see duplicate/blacklist warnings during entry.

### Important design decision

The recruiter should be able to create a candidate even if there is a possible duplicate or blacklist match, but the system should show a strong warning and require HR/manager review before activation.

That avoids false-positive dead ends while still protecting the business from known bad returns.

---

## 5.3 Status Lifecycle

The status system is the backbone of the product.

### Recommended statuses

| Status | Meaning |
|---|---|
| Lead / Interested | Person is known, but not yet qualified |
| Candidate | Basic profile exists and recruiter is processing them |
| Screened | Candidate has passed initial review/interview |
| Test Scheduled | Candidate has an upcoming test/interview/work trial |
| Tested Candidate | Candidate has completed test but is not active yet |
| Pending | Waiting for documents, approval, assignment, or manager decision |
| Active Worker | Approved and assigned/available for work |
| Archived | Inactive, but not blocked from future rehire |
| Blacklisted | Rehire or cooperation requires special approval or is blocked |

### Status transition rules

| From | To | Allowed by | Required check |
|---|---|---|---|
| Lead | Candidate | Recruiter | Minimum profile fields |
| Candidate | Screened | Recruiter | Screening result |
| Screened | Test Scheduled | Recruiter / Coordinator | Project/worksite selected |
| Test Scheduled | Tested Candidate | Coordinator / HR | Test result |
| Tested Candidate | Pending | HR / Coordinator | Missing documents or approval |
| Pending | Active Worker | HR / Manager | Checklist complete, documents valid |
| Active Worker | Archived | HR / Manager | Exit reason |
| Any | Blacklisted | Manager / Admin | Reason and approval |
| Blacklisted | Candidate/Pending | Admin only | Exceptional override reason |

### Hard-stop rules

The system should not allow Active Worker status if:

- required identity document is missing;
- required work/residence permit is missing or expired;
- required medical/safety document is missing or expired;
- required project checklist is incomplete;
- unresolved blacklist match exists;
- unresolved duplicate match exists where HR review is required.

### Inactive / archive reasons (interview)

When a person becomes inactive, the system should require a reason and a date:

- sick;
- quit / left;
- suspended;
- military service;
- other (free text).

Routing rule: a leaver who left in good standing and may return should be routed **back to the recruiter** (not hard-archived), so they re-enter the pipeline cleanly on return. A hard exit (e.g. blacklist-worthy) does not route back.

---

## 5.4 Document Management

This module manages uploaded documents, document status, and expiry alerts.

### Document types

- identity card;
- passport;
- residence permit;
- work permit;
- medical certificate;
- safety training confirmation;
- employment contract;
- project-specific forms;
- certificate/license, for example forklift certificate;
- other HR attachment.

### Document fields

- document type;
- person;
- file attachment;
- issue date;
- expiry date;
- status;
- uploaded by;
- verified by;
- verification date;
- rejection reason;
- notes;
- visibility level.

### Document statuses

- missing;
- uploaded;
- awaiting verification;
- verified;
- rejected;
- expiring soon;
- expired.

### Expiry alert rules

Default alerts:

- 30 days before expiry;
- 15 days before expiry;
- on expiry date;
- after expiry until resolved.

Recipients:

- HR admin;
- assigned coordinator;
- responsible manager;
- optionally recruiter, depending on workflow.

---

## 5.5 Approval Checklists

The approval system ensures that nobody becomes active without required checks.

### Checklist types

- global activation checklist;
- project/worksite-specific checklist;
- role/position-specific checklist;
- reactivation checklist for archived workers;
- blacklist-review checklist.

### Example global activation checklist

- personal data complete;
- identity document uploaded and verified;
- work/residence permit uploaded and valid, if applicable;
- medical certificate uploaded and valid;
- safety training completed;
- contract uploaded/signed;
- duplicate check resolved;
- blacklist check resolved;
- assigned project/worksite selected;
- final approval by HR/manager.

### Checklist behavior

- show missing items clearly on the person profile;
- block Active status when critical items are missing;
- allow non-critical warnings without blocking;
- record who approved each checklist item;
- store approval history in audit log.

---

## 5.6 Duplicate and Blacklist Detection

This is a risk-control module and should be built early.

### Match signals

| Signal | Strength | Notes |
|---|---:|---|
| Passport number | High | Best match for non-EU workers |
| National ID number | High | Useful for EU workers |
| Residence permit number | High | Good supporting match |
| Full name + birth date | Medium/high | Useful fallback, can produce false positives |
| Phone number | Medium | Useful but may change |
| Email | Low/medium | Less reliable for blue-collar workforce |
| Hash of identifiers | High for retained matching | Useful after anonymization, must be handled carefully |

### Duplicate check result types

- no match;
- possible duplicate;
- strong duplicate;
- blacklist match;
- archived-person match;
- hash-only retained-risk match.

### Required workflow

1. User enters person data.
2. System checks live records and retained hash records.
3. If match exists, show warning.
4. Allow saving as Pending, but require HR/manager review before activation.
5. Store the review decision.
6. Audit the lookup and decision.

### Blacklist record fields

- person;
- blacklist status;
- category;
- reason text;
- created by;
- approved by;
- date added;
- review date;
- removal/override reason;
- visibility level.

### Blacklist categories, initial proposal

- no-show / repeated absence;
- alcohol or substance issue;
- aggression / violence;
- theft;
- property damage;
- serious rule violation;
- document fraud;
- unreliable / repeated breach;
- other.

---

## 5.7 Partner Company / Project / Worksite Assignment

Since CorvinumEU does not need accommodation or accounting integration in this project, the operational assignment structure becomes more important.

### Entities

- partner company;
- project;
- worksite;
- position/job role;
- assignment;
- coordinator responsibility;
- recruiter responsibility.

### Assignment fields

- person;
- partner company;
- project;
- worksite;
- position;
- start date;
- end date;
- assignment status;
- coordinator;
- manager;
- notes.

### Assignment statuses

- planned;
- active;
- paused;
- completed;
- cancelled;
- failed/no-show.

### Why this matters

This replaces the Jober-specific accommodation logic with a cleaner operational model: who is connected to which partner/project/worksite, under whose responsibility, and in what state.

---

## 5.8 Equipment & Issued Items

CorvinumEU does not manage accommodation or transport logistics, but it **does** issue physical items to workers and needs to recover their cost when they are not returned. This was confirmed in the interview and reverses the v0.3 exclusion of equipment.

### Item types

- shirt / t-shirt;
- trousers;
- footwear;
- tool;
- medical item;
- other.

### Captured per item

- type and description;
- size (e.g. footwear roughly 35–50, tops up to 5XL — a size reference reduces entry errors);
- value;
- issue date and who issued it;
- returned / not returned, with return date and condition;
- linked deduction when an unreturned item is charged.

### Required capabilities

- issue an item to a person with size and value;
- list issued items per person with return status;
- mark an item returned, or charge it as a deduction (creating a linked ledger entry in module 5.10);
- retain per-person issued-item history so returning workers cannot dispute prior deductions.

### Why this matters

Workers sometimes leave after a day or two with issued clothing, shoes, or medical items. Recording value at issue and charging unreturned items closes a real, recurring cash leak — and the retained history prevents disputes on re-hire.

---

## 5.9 Coordinator Mobile View

Coordinators need a fast operational view, not a full desktop admin system squeezed onto a phone like some punishment ritual.

### Mobile-first coordinator features

- list of assigned workers;
- quick search;
- open worker profile;
- call button;
- WhatsApp/message shortcut;
- quick status update;
- add note/activity;
- see document validity status, not necessarily full document files;
- see today’s tasks;
- see pending issues;
- see project/worksite assignment;
- issue or return equipment;
- mark a problem event.

### Mobile view priorities

1. Find worker fast.
2. Contact worker fast.
3. See if worker is allowed/ready/blocked.
4. Add operational note.
5. Escalate issue to HR/manager.

### Later v2 possibility

Offline-capable PWA mode may be useful if coordinators often work in areas with weak internet.

---

## 5.10 Advance & Deduction Ledger

This is the operational core surfaced by the interview: workers take **cash advances against future wages**, the office summarises them weekly, distributes cash, and deducts the amounts from pay. The same ledger records **deductions** (clothing, medical, equipment, advance repayment) and **additions** (travel / fuel money).

> **Financial boundary.** This is per-worker operational cash tracking netted against pay — not accounting, payroll, invoicing, or P&L. The boundary needs client sign-off (13.1).

### Explicit-field model (no signed amounts)

Money is modelled with explicit fields so that **cash movement** and **payroll effect** are never conflated in one signed number. Every entry stores a positive magnitude plus its meaning.

- `entry_type` — what happened:
  - `CASH_ADVANCE` — cash physically handed to the worker now, against future pay;
  - `PAY_DEDUCTION` — an amount to be taken from pay (e.g. clothing/equipment loss, advance recovery);
  - `PAY_ADDITION` — an amount to be added to pay (e.g. travel / fuel).
- `amount` — always a **positive `Decimal`** (never negative), with `currency`.
- `pay_effect` — how it touches payroll: `NONE`, `DEDUCT`, or `ADD`. Typical mapping: `CASH_ADVANCE → DEDUCT` (recovered later), `PAY_DEDUCTION → DEDUCT`, `PAY_ADDITION → ADD`. `NONE` is reserved for entries with no payroll impact.
- `settlement_status` — lifecycle: `OPEN` → `INCLUDED_IN_CYCLE` → `DEDUCTED`, or `CANCELLED`.

Worked examples:

- a €100 advance is one `CASH_ADVANCE`, `amount = 100`, `pay_effect = DEDUCT`, `settlement_status = OPEN`; when recovered it is assigned to a specific 20th-to-20th cycle and moves `INCLUDED_IN_CYCLE → DEDUCTED`. It is never stored as `-100`.
- an unreturned jacket is one `PAY_DEDUCTION`, `amount = 25`, `pay_effect = DEDUCT`, linked to the issued item.
- fuel money is one `PAY_ADDITION`, `amount = 30`, `pay_effect = ADD`.

### Categories

- cash_advance;
- clothing;
- footwear;
- equipment;
- medical;
- travel_fuel;
- other.

### Cycle and rhythm (interview)

- advances are summarised **Thursday afternoon**, by company and by person;
- the summary total is handed to the cash provider; cash is distributed **Friday**;
- amounts are reconciled against pay over a **20th-to-20th** monthly cycle;
- entries are **manual** in MVP (the office accepts this, with room to speed up later).

### Ledger rules to define (must be fixed before build)

These are not optional details; ambiguity here produces wrong money. Each needs an exact, written rule:

- **timezone and Thursday cut-off time** — one canonical timezone (proposed: Europe/Bratislava) and an exact cut-off (interview said "Thursday afternoon" — confirm e.g. 14:00);
- **which Friday a late entry belongs to** — entries after the Thursday cut-off (proposed) roll to the next week's Friday, never retro-inserted into a summary already sent;
- **cycle calculation across month/year boundaries** — define the 20th-to-20th window as date math in the canonical timezone (inclusive/exclusive boundary stated), correct across December→January;
- **correction vs deletion** — no hard deletes; pre-inclusion edits are audit-logged, post-inclusion changes happen only via reversal;
- **cancellation and reversal** — `CANCELLED` for entries never acted on; a reversal entry (opposite `pay_effect`) for entries already `DEDUCTED`;
- **partial recovery** — decide whether an advance may be recovered across several cycles. If yes, the model needs either a `recovered_amount`/`remaining_amount` on the advance or linked recovery `PAY_DEDUCTION` entries referencing it (`recovers_advance_id`). This is a model-affecting decision (13.3);
- **immutability after cycle inclusion** — once `INCLUDED_IN_CYCLE`/`DEDUCTED`, the entry is locked; only reversal entries change the net;
- **Excel/CSV summary layout** — define exact columns and ordering for the Thursday summary and the cycle report (proposed columns: company, person, date, entry_type, category, amount, pay_effect, cycle, settlement_status).

### Required capabilities

- record advances, deductions, and additions against a person and their company/project;
- weekly summary (Thursday cut-off) by company and person;
- 20th-to-20th cycle report per person and company;
- deduction report and a "deducted from salary" flag per entry;
- search by person or company over a date range;
- restrict visibility/entry to office/HR/management roles; audit-log every entry.

### Why this matters

Today this lives in Excel and memory, advances are sometimes not deducted, and there is no reliable Thursday summary. An explicit-field ledger with weekly and cycle views removes the single biggest source of operational and financial error for CorvinumEU.

---

## 5.11 Operational Reporting

The first reports should support daily operations, not finance.

### MVP reports

- active workers by partner/project/worksite;
- candidates by pipeline status;
- candidates awaiting test/interview;
- tested candidates awaiting decision;
- pending activations;
- missing documents;
- expiring documents;
- expired documents;
- duplicate/blacklist review queue;
- workers by coordinator;
- candidates by recruiter;
- archived workers by reason;
- blacklisted records by category;
- advances/deductions by person and company (weekly and 20–20 cycle);
- equipment issued vs. returned, with outstanding value.

### Later reports

- recruitment conversion rates;
- recruiter performance trend;
- coordinator workload trend;
- project staffing trend;
- document compliance trend;
- average time from candidate to active worker;
- drop-off reasons.

---

## 5.12 Admin, Security, GDPR, Audit

This system stores sensitive HR data, identity documents, permits, and possibly blacklist information. Security cannot be duct-taped on later without everyone pretending they meant to do that.

### Admin features

- user management;
- role management;
- permission settings;
- project/worksite settings;
- document type settings;
- checklist template settings;
- status settings;
- notification settings;
- equipment item type and value settings;
- advance/deduction category settings;
- retention/anonymization settings;
- audit log view.

### Security baseline

- two-factor authentication for HR/admin/manager roles;
- strong password policy;
- session security;
- role-based access control;
- audit log for sensitive views and edits;
- encrypted backups;
- staging and production environments;
- daily backups;
- EU-based hosting;
- least-privilege access to documents.

### GDPR features

- retention policies by record type;
- candidate anonymization after configured period;
- document deletion rules;
- hash-based re-application detection where legally approved;
- restricted access to advance/deduction financial data and to retained equipment-deduction history;
- audit log for sensitive access;
- export capability for data subject requests;
- deletion/anonymization review queue.

---

# 6. Data model / database design

This is the first technical design pass. It is not final schema, but it gives us the backbone.

## 6.1 Core entities

### User

Represents an internal system user.

Fields:

- id;
- name;
- email;
- phone;
- role;
- status;
- two_factor_enabled;
- last_login_at;
- created_at;
- updated_at.

Relationships:

- has many created people;
- has many assigned tasks;
- has many audit log entries;
- may be recruiter, coordinator, HR admin, manager, observer, or system admin.

---

### Person

Represents a candidate, worker, archived worker, or blacklisted person.

Fields:

- id;
- public_reference_code;
- first_name;
- last_name;
- full_name_normalized;
- birth_date;
- birth_place;
- nationality;
- gender, optional;
- primary_phone;
- secondary_phone;
- email;
- permanent_address;
- current_address, optional;
- emergency_contact_name;
- emergency_contact_phone;
- spoken_languages;
- preferred_language, SK / HU;
- payment_method, cash / bank_transfer;
- bank_account_encrypted, optional;
- has_children;
- number_of_children, optional;
- smokes;
- drinks;
- invalidity_status, optional;
- tax_bonus_note, optional;
- current_status;
- status_reason;
- recruiter_id;
- coordinator_id;
- created_at;
- updated_at;
- archived_at;
- anonymized_at.

Relationships:

- has many identifiers;
- has many documents;
- has many status history entries;
- has many assignments;
- has many issued items;
- has many ledger entries;
- has many notes;
- has many checklist results;
- may have blacklist record;
- may have duplicate matches.

---

### PersonIdentifier

Stores sensitive identity/permit identifiers separately from the main person table.

Fields:

- id;
- person_id;
- identifier_type;
- identifier_value_encrypted;
- identifier_value_hash;
- country;
- issue_date;
- expiry_date;
- status;
- created_at;
- updated_at.

Identifier types:

- passport;
- national_id;
- residence_permit;
- work_permit;
- tax_id;
- social_security_id;
- other.

Notes:

- exact values should be encrypted;
- hash values should be used for duplicate/blacklist matching;
- access should be restricted and audited.

---

### Document

Stores metadata about uploaded documents.

Fields:

- id;
- person_id;
- document_type_id;
- file_storage_key;
- original_filename;
- issue_date;
- expiry_date;
- status;
- uploaded_by_user_id;
- verified_by_user_id;
- verified_at;
- rejected_by_user_id;
- rejected_at;
- rejection_reason;
- visibility_level;
- created_at;
- updated_at.

---

### DocumentType

Configurable list of document types.

Fields:

- id;
- name;
- code;
- is_required_by_default;
- has_expiry_date;
- default_alert_days;
- allowed_roles_to_view;
- allowed_roles_to_upload;
- created_at;
- updated_at.

---

### PartnerCompany

Represents a client/partner company where workers may be assigned.

Fields:

- id;
- name;
- company_id_number, optional;
- vat_number, optional;
- address;
- contact_person;
- contact_email;
- contact_phone;
- status;
- notes;
- created_at;
- updated_at.

---

### Project

Represents a project or cooperation under a partner company.

Fields:

- id;
- partner_company_id;
- name;
- description;
- status;
- default_manager_id;
- default_coordinator_id;
- start_date;
- end_date;
- notes;
- created_at;
- updated_at.

---

### Worksite

Represents a physical workplace/site.

Fields:

- id;
- partner_company_id;
- project_id, optional;
- name;
- address;
- contact_person;
- contact_phone;
- notes;
- status;
- created_at;
- updated_at.

---

### Position

Represents a job role or position.

Fields:

- id;
- name;
- code;
- description;
- required_language_level;
- required_documents;
- required_certificates;
- status;
- created_at;
- updated_at.

---

### Assignment

Connects a person to a partner/project/worksite/position.

Fields:

- id;
- person_id;
- partner_company_id;
- project_id;
- worksite_id;
- position_id;
- coordinator_id;
- manager_id;
- start_date;
- end_date;
- status;
- reason;
- notes;
- created_at;
- updated_at.

---

### IssuedItem

Clothing, footwear, tools, or medical items issued to a person, with value and return tracking.

Fields:

- id;
- person_id;
- item_type;
- description;
- size, optional;
- value;
- currency;
- issued_date;
- issued_by_user_id;
- is_returned;
- returned_date;
- condition_on_return;
- deduction_ledger_entry_id, optional, set when an unreturned item is charged;
- notes;
- created_at;
- updated_at.

Item types:

- shirt / t-shirt;
- trousers;
- footwear;
- tool;
- medical;
- other.

Notes:

- recorded value enables cost recovery when an item is not returned;
- per-person history is retained so returning workers cannot dispute prior deductions.

---

### LedgerEntry

A single cash advance, deduction, or addition against a person. Operational cash tracking, not accounting. Cash movement and payroll effect are separate explicit fields — no signed amounts.

Fields:

- id;
- person_id;
- partner_company_id;
- entry_type — CASH_ADVANCE | PAY_DEDUCTION | PAY_ADDITION;
- category — cash_advance | clothing | footwear | equipment | medical | travel_fuel | other;
- amount — positive Decimal;
- currency;
- pay_effect — NONE | DEDUCT | ADD;
- settlement_status — OPEN | INCLUDED_IN_CYCLE | DEDUCTED | CANCELLED;
- entry_date — when the cash moved / the event occurred;
- distribution_friday — which Friday the cash was/will be handed out (CASH_ADVANCE);
- recovery_cycle_start — the 20th-to-20th cycle this is applied/recovered in;
- related_issued_item_id, optional — links an equipment-loss PAY_DEDUCTION to the item;
- recovers_advance_id, optional — set if partial-recovery-as-linked-entries is chosen (13.3);
- reversal_of_entry_id, optional — set on reversal entries;
- locked — true once INCLUDED_IN_CYCLE/DEDUCTED (immutable thereafter);
- entered_by_user_id;
- notes;
- created_at;
- updated_at.

Notes:

- amount is always positive; direction is carried by `pay_effect`, not by sign;
- a CASH_ADVANCE is recorded when paid and later marked recovered in a specific cycle (settlement_status);
- an equipment-loss deduction is a PAY_DEDUCTION linked via `related_issued_item_id`;
- entered manually in MVP; the Thursday summary and 20th-to-20th cycle report are built from these entries;
- once `locked`, corrections happen only via reversal entries (see 5.10 ledger rules);
- visibility restricted to office/HR/management roles.

---

### StatusHistory

Records every status transition.

Fields:

- id;
- person_id;
- from_status;
- to_status;
- changed_by_user_id;
- changed_at;
- reason;
- notes;
- approval_id, optional.

---

### ChecklistTemplate

Defines required checks for activation or project assignment.

Fields:

- id;
- name;
- scope_type;
- project_id, optional;
- worksite_id, optional;
- position_id, optional;
- is_active;
- created_at;
- updated_at.

Scope types:

- global_activation;
- project_activation;
- worksite_activation;
- position_activation;
- reactivation;
- blacklist_review.

---

### ChecklistItemTemplate

Defines individual checklist items.

Fields:

- id;
- checklist_template_id;
- label;
- description;
- is_required;
- blocks_activation;
- document_type_id, optional;
- sort_order;
- created_at;
- updated_at.

---

### PersonChecklistItem

Stores checklist completion per person.

Fields:

- id;
- person_id;
- checklist_item_template_id;
- status;
- completed_by_user_id;
- completed_at;
- rejected_by_user_id;
- rejected_at;
- rejection_reason;
- notes.

---

### TestEvent / ScreeningEvent

Stores interview/test/work trial events.

Fields:

- id;
- person_id;
- project_id;
- worksite_id;
- scheduled_at;
- event_type;
- coordinator_id;
- recruiter_id;
- status;
- result;
- result_reason;
- notes;
- created_at;
- updated_at.

Event statuses:

- scheduled;
- completed;
- no_show;
- cancelled;
- rescheduled.

Results:

- passed;
- failed;
- rejected;
- pending decision.

---

### ActivityNote

Timeline notes attached to a person.

Fields:

- id;
- person_id;
- author_user_id;
- note_type;
- body;
- visibility_level;
- created_at;
- updated_at.

Note types:

- general;
- call;
- meeting;
- warning;
- coordinator_note;
- HR_note;
- manager_note;
- system_event.

---

### DuplicateMatch

Stores possible duplicate checks.

Fields:

- id;
- person_id;
- matched_person_id, optional;
- matched_hash_id, optional;
- match_type;
- match_strength;
- status;
- reviewed_by_user_id;
- reviewed_at;
- review_decision;
- review_note;
- created_at.

Statuses:

- open;
- confirmed_duplicate;
- false_positive;
- merged;
- ignored_with_reason.

---

### BlacklistRecord

Stores blacklist status and sensitive reason data.

Fields:

- id;
- person_id;
- category;
- reason_text;
- status;
- created_by_user_id;
- approved_by_user_id;
- approved_at;
- removed_by_user_id;
- removed_at;
- removal_reason;
- visibility_level;
- created_at;
- updated_at.

---

### Task

Action items for users.

Fields:

- id;
- assigned_to_user_id;
- related_person_id, optional;
- related_project_id, optional;
- title;
- description;
- task_type;
- priority;
- due_date;
- status;
- created_by_user_id;
- completed_at;
- created_at;
- updated_at.

Task types:

- document_expiry;
- missing_document;
- activation_approval;
- duplicate_review;
- blacklist_review;
- test_followup;
- weekly_advance_summary;
- equipment_return;
- coordinator_action;
- general.

---

### Notification

In-app, internal alerts to system users (staff).

Fields:

- id;
- user_id;
- title;
- body;
- notification_type;
- related_entity_type;
- related_entity_id;
- read_at;
- created_at.

---

### AuditLog

Immutable system activity log.

Fields:

- id;
- actor_user_id;
- action;
- entity_type;
- entity_id;
- before_json;
- after_json;
- ip_address;
- user_agent;
- created_at.

Must log:

- login/logout;
- failed login;
- person create/update/delete/anonymize;
- document view/upload/delete/verify/reject;
- identifier view/update;
- status change;
- blacklist create/update/remove/view;
- duplicate match review;
- advance/deduction ledger entry;
- equipment issue and return;
- permission changes;
- export actions;
- admin setting changes.

---

### RetentionPolicy

Configuration for GDPR retention and anonymization.

Fields:

- id;
- record_type;
- status_scope;
- retention_days;
- action_after_retention;
- requires_review_before_action;
- is_active;
- created_at;
- updated_at.

Actions:

- delete;
- anonymize;
- archive;
- flag_for_review.

---

## 6.2 Relationship summary

- One `Person` has many `Documents`.
- One `Person` has many `PersonIdentifiers`.
- One `Person` has many `Assignments`.
- One `Assignment` belongs to one `PartnerCompany`, one `Project`, one `Worksite`, and one `Position`.
- One `Person` has many `StatusHistory` records.
- One `Person` may have one active `BlacklistRecord`.
- One `Person` may have many `DuplicateMatch` records.
- One `ChecklistTemplate` has many `ChecklistItemTemplates`.
- One `Person` has many `PersonChecklistItems`.
- One `Person` has many `IssuedItems`.
- One `Person` has many `LedgerEntries`; a `LedgerEntry` may reference one `IssuedItem`.
- One `User` can be recruiter, coordinator, HR admin, manager, observer, or system admin.
- Every sensitive action creates an `AuditLog` entry.

---

# 7. Screen-by-screen UX design

This section describes the first usable screens. We can later convert this into wireframes.

## 7.0 Design language (corvinum.eu alignment)

The management app must read as the same product as **corvinum.eu**, and specifically as an extension of the **admin panel already embedded in that public site**. We adopt the site's existing design system rather than inventing one. On the white-label model (12.4), this design system is CorvinumEU's per-client theming layer over the shared core.

### Carry over directly from corvinum.eu

- brand: CORVINUM EU wordmark and raven logo; tone "industrial reliability, professional precision";
- **bilingual SK/HU** with a language toggle (public side defaults SK; admin dialogs are HU). Every label is stored as an HU+SK pair, matching the site's dual-field job editor;
- **light + dark theme** with a toggle;
- **Google Material Symbols** iconography — reuse the same icon set;
- premium-industrial aesthetic: clean sans-serif, generous spacing, card-based sections, a single strong accent over a neutral/dark base, industrial photography in headers where appropriate.

### Component patterns already present on the site (mirror these)

- modal dialogs with a close affordance;
- primary buttons with a trailing "sync" spinner/loading state;
- tabbed panels (the applications inbox uses three tabs);
- table list views;
- badge chips (None / Urgent / New);
- info chips (icon + label);
- image upload zones (drag/drop, JPG/PNG/WEBP, max 5 MB);
- CV upload (PDF/DOC/DOCX, max 5 MB).

### Existing admin components — reuse candidates, pending audit

corvinum.eu already ships these in the brand's design language:

- admin login, **2FA** (QR + authenticator, 6-digit code), password reset, "set password / account setup";
- security-settings panel;
- applications inbox (job-specific applicants / general applicants / partner inquiries) — a natural seed for the recruitment pipeline inbox;
- bilingual job add/edit CRUD with badges and info chips.

These map onto v0.4 features (login + 2FA, show-password, account-setup link, CV storage, recruitment inbox). **But "already exists" is not "safe to transplant."** What the public site proves is that the *design* exists; whether the *code* is reusable — visually, structurally, or at all — is an open question that must be answered before any of it is counted as done work.

#### Reuse audit (gate before relying on any of these)

For each candidate component, determine:

- **Ownership** — which repository actually owns it (the public-site repo? a separate admin repo? a third party?), and do we have rights to the source.
- **Stack** — vanilla JS, Django, or something else; does it fit the npm-free Django/htmx target, or would it drag in a toolchain we're trying to avoid.
- **Auth compatibility** — is its authentication model compatible with the platform's RBAC, sessions, and 2FA, or is it a separate auth world that would need bridging.
- **Production quality** — is the code production-grade (tested, maintained, secure), or a marketing-site prototype that happens to render well.
- **Asset/licence reuse** — can the CSS, fonts, icons, and images be reused **legally and technically** (licences, third-party fonts/icon sets, asset hosting).
- **Supply-chain rules** — does it meet the project's current supply-chain / dependency-hardening rules (no disallowed packages, pinned and vetted dependencies).

Outcome of the audit per component: **reuse as-is**, **reuse the design only (re-implement in our stack)**, or **rebuild**. Default to "design only" until proven otherwise — visual continuity is the cheap, safe win; transplanting code is the claim that needs evidence.

### Implementation note (npm-free Django/htmx)

The public site appears to use a Tailwind + Material-Symbols toolchain. Our build is npm-free Django/htmx, so we replicate the look by lifting the site's CSS tokens into our own stylesheet and using the same Material Symbols icon set — matching the design system without adopting its build pipeline.

**Material Symbols must not be loaded from Google (or any CDN) at runtime.** Project supply-chain rules prohibit CDN runtime assets and require human-controlled external artifacts. For CorvinumEU:

- obtain the required Material Symbols font files through the **asset-request process** (not a direct download baked into the build);
- record **source, licence, version, and checksum** for the obtained files;
- **vendor them locally** in the repository;
- **serve them from the application**, never from `fonts.googleapis.com` / `fonts.gstatic.com` or any other CDN.

The same rule applies to any other external font, icon set, or asset pulled from the corvinum.eu design system: vendored, provenance-recorded, app-served. No runtime third-party fetches.

### Tokens to lift from the live corvinum.eu CSS (to be filled during build)

- primary / accent color(s);
- neutral and background scale (light + dark);
- heading and body font families;
- border-radius and elevation/shadow scale;
- logo assets (light/dark variants).

This document fixes the design *direction*; exact hex and font values are copied from the live site CSS during build.

### Watch-out

The public site's job cards include an "Ubytovanie / bus" (accommodation / bus) info chip. That is a marketing benefit label on job ads, not an operational feature — it does not reintroduce accommodation or transport modules into the management system.

---

## 7.1 Login screen

Purpose:

- secure system entry.

Elements:

- email;
- password, with a show/hide toggle;
- 2FA prompt where enabled;
- forgot password;
- magic-link login option;
- login error handling.

Notes:

- HR/admin/manager roles should require 2FA.

---

## 7.2 Main dashboard

Purpose:

- role-specific overview after login.

Widgets by role:

### Recruiter

- my candidates;
- candidates needing follow-up;
- duplicate/blacklist warnings;
- tests/interviews scheduled;
- recently created candidates.

### Coordinator

- my active workers;
- workers with urgent issues;
- expiring documents for assigned workers;
- today's test/interview events;
- quick search.

### HR Admin

- pending document verification;
- pending activations;
- missing critical documents;
- expiring documents;
- duplicate/blacklist review queue.

### Manager

- active workers by project;
- pending approvals;
- this week's advance summary (Thursday cut-off) by company;
- open compliance risks;
- blacklist review queue.

---

## 7.3 People list

Purpose:

- central searchable list of candidates and workers.

Columns:

- name;
- status;
- phone;
- nationality;
- recruiter;
- coordinator;
- project/worksite;
- document status;
- duplicate/blacklist indicator;
- last activity;
- actions.

Filters:

- status;
- recruiter;
- coordinator;
- project;
- worksite;
- nationality;
- document state;
- duplicate status;
- blacklist status;
- created date;
- updated date.

Quick actions:

- open profile;
- call;
- WhatsApp/message;
- add note;
- change status, permission-dependent.

---

## 7.4 New person wizard

Purpose:

- guided candidate creation with duplicate checking.

Steps:

1. Basic identity
2. Contact data
3. Identifiers
4. Intake details (children, smoking, drinking, invalidity, tax bonus, payment method)
5. Recruitment source
6. Upload CV and initial documents, optional
7. Initial company/project interest
8. Duplicate/blacklist check result
9. Save as candidate/pending

Important behavior:

- duplicate check should happen before final save;
- strong match should warn loudly;
- blacklist match should require manager/HR review;
- creation should not be impossible because of possible false positives.

---

## 7.5 Person profile

Purpose:

- single source of truth for a person.

Header:

- name;
- photo, optional;
- current status;
- phone;
- assigned recruiter;
- assigned coordinator;
- current project/worksite;
- warning badges.

Tabs:

1. Overview
2. Personal data
3. Identifiers
4. Documents
5. Assignments
6. Equipment / issued items
7. Advances / deductions
8. Checklist / approvals
9. Tests / interviews
10. Activity timeline
11. Duplicate / blacklist
12. Audit, admin-only

Warnings:

- missing required document;
- expiring document;
- expired document;
- unresolved duplicate;
- unresolved blacklist match;
- activation blocked.

---

## 7.6 Document verification queue

Purpose:

- HR can process uploaded documents efficiently.

Columns:

- person;
- document type;
- uploaded date;
- uploaded by;
- expiry date;
- status;
- assigned project;
- action.

Actions:

- view document;
- verify;
- reject with reason;
- request replacement;
- edit expiry date;
- add note.

---

## 7.7 Activation approval screen

Purpose:

- HR/manager decides whether a person can become active.

Sections:

- person summary;
- duplicate/blacklist status;
- required documents;
- project/worksite checklist;
- missing items;
- notes;
- approve / reject buttons.

Behavior:

- approval button disabled if hard-stop items are missing;
- rejection requires reason;
- approval creates audit log;
- approved user moves to Active Worker.

---

## 7.8 Duplicate / blacklist review queue

Purpose:

- central queue for risky records.

Columns:

- new person;
- matched person/record;
- match reason;
- match strength;
- current status;
- assigned reviewer;
- created date;
- action.

Actions:

- confirm duplicate;
- mark false positive;
- merge records, later phase;
- approve continuation;
- keep pending;
- blacklist;
- add review note.

---

## 7.9 Partner company page

Purpose:

- manage partner/client companies.

Sections:

- company details;
- contact people;
- projects;
- worksites;
- active assignments;
- historical assignments;
- notes.

---

## 7.10 Project / worksite page

Purpose:

- manage operational assignment context.

Sections:

- project/worksite details;
- assigned coordinator;
- required checklist;
- active workers;
- pending candidates;
- documents required for this project;
- notes.

---

## 7.11 Equipment issuance screen

Purpose:

- issue clothing/footwear/tools/medical items and track returns and cost recovery.

Sections:

- issue item to a person: type, size, value, date;
- per-person issued-items list with returned / not-returned status;
- mark item returned, or charge it as a deduction (creates a ledger entry);
- size reference (footwear ~35–50, tops up to 5XL) to reduce entry errors;
- item types and default values come from admin settings.

Behavior:

- charging an unreturned item creates a linked `LedgerEntry` deduction;
- issued-item history is retained per person and cannot be silently erased.

---

## 7.12 Coordinator mobile screen

Purpose:

- mobile-first field operations.

Views:

- My workers;
- Today;
- Urgent issues;
- Search;
- Worker profile quick view;
- Add note;
- Change status;
- Issue / return equipment;
- Contact shortcuts (call, Messenger).

Worker card:

- name;
- photo, optional;
- phone;
- project/worksite;
- status;
- document state;
- issue badges;
- call/message buttons.

---

## 7.13 Advance & deduction screen

Purpose:

- record cash advances, deductions, and additions, and produce the weekly and cycle summaries.

Sections:

- entry form: person, company/project, entry_type (CASH_ADVANCE / PAY_DEDUCTION / PAY_ADDITION), category, positive amount, date, note;
- per-person ledger with running total and "deducted from salary" flag;
- weekly summary (Thursday cut-off): by company and person, totals to hand to the cash provider for Friday;
- 20th-to-20th cycle report per person/company;
- deduction report (clothing, medical, equipment, advance repayment);
- search by person or company over a date range.

Behavior:

- direction is shown by entry_type + pay_effect, not by a signed number; amounts are always positive;
- entries are manual in MVP;
- the Thursday summary feeds the Friday cash hand-out;
- visible only to office/HR/management roles; every entry is audit-logged.

---

## 7.14 Reports screen

Purpose:

- operational overview.

Report groups:

- people and statuses;
- recruitment pipeline;
- documents and compliance;
- assignments;
- advances and deductions;
- equipment / issued items;
- recruiters/coordinators;
- duplicates/blacklist;
- activity/audit.

Export:

- CSV/Excel export for selected reports;
- export must be permission-controlled and audit logged.

---

## 7.15 Admin settings

Purpose:

- configure system without code changes.

Settings:

- users;
- roles;
- permissions;
- status labels;
- document types;
- checklist templates;
- projects/worksites;
- equipment item types and default values;
- advance/deduction categories;
- notification rules;
- retention policies;
- audit log;
- backup status;
- system health.

---

# 8. Key workflows

## 8.1 Candidate intake workflow

1. Recruiter creates person.
2. System checks duplicate/blacklist signals.
3. Recruiter fills basic data.
4. Candidate enters Candidate status.
5. Recruiter schedules screening/test.
6. Coordinator/HR is notified if needed.

---

## 8.2 Test / interview workflow

1. Recruiter schedules test/interview event.
2. Coordinator sees event in dashboard/mobile view.
3. Candidate attends or no-shows.
4. Coordinator records result.
5. Candidate moves to Tested Candidate, Pending, Archived, or Blacklisted depending on result.

---

## 8.3 Activation workflow

1. Candidate passes test/screening.
2. HR checks required documents.
3. System checks project/worksite checklist.
4. Duplicate/blacklist review must be resolved.
5. HR/manager approves activation.
6. Person becomes Active Worker.
7. Assignment is created or confirmed.

---

## 8.4 Document expiry workflow

1. System scans documents daily.
2. Document approaching expiry creates alert/task.
3. HR/coordinator receives notification.
4. Replacement document is uploaded.
5. HR verifies replacement.
6. Task closes automatically.

---

## 8.5 Blacklist workflow

1. Coordinator/HR proposes blacklist.
2. Reason category and explanation are required.
3. Manager/Admin reviews.
4. If approved, person is blacklisted.
5. Future attempts to create matching person show warning.
6. Access to reason is restricted and audited.

---

## 8.6 Archive / reactivation workflow

1. Worker leaves or candidate becomes inactive.
2. HR/manager archives record with reason.
3. Record remains searchable according to retention rules.
4. If person returns, system detects archived match.
5. HR decides whether to reactivate or create new cycle.

---

## 8.7 Advance & deduction workflow

1. Through the week, a worker requests a cash advance against wages.
2. Office records the advance against the person and their company/project.
3. Thursday afternoon, the system produces the weekly summary by company and person.
4. The total is handed to the cash provider; cash is distributed Friday.
5. Deductions (clothing, medical, equipment, advance recovery) are PAY_DEDUCTION entries; additions (travel/fuel) are PAY_ADDITION entries — amounts positive, direction carried by `pay_effect`.
6. At payroll, recorded amounts net against the worker's pay over the 20th-to-20th cycle.
7. Entries are manual in MVP, restricted to office/HR/management, and audit-logged.

---

## 8.8 Equipment issuance & recovery workflow

1. Coordinator/HR issues an item (clothing, footwear, tool, medical) with size and value.
2. The item is recorded against the person.
3. On exit or return, the item is marked returned, or
4. if not returned, it is charged as a deduction, creating a linked ledger entry.
5. The issued-item and deduction history is retained per person so returning workers cannot dispute it.

---

# 9. MVP feature list

## 9.1 MVP goal

Deliver a working internal HR operations system that replaces scattered candidate/worker tracking and makes document/status/assignment risks visible.

## 9.2 MVP must-have features

### People and roles

- user login;
- roles and permissions;
- candidate/worker profile;
- recruiter assignment;
- coordinator assignment;
- HR/admin access;
- observer/read-only role.

### Pipeline and status

- status lifecycle;
- status history;
- status transition permissions;
- pending/active/archive/blacklist states;
- reason required for sensitive transitions.

### Documents

- document upload;
- document metadata;
- document expiry date;
- document verification;
- missing/expiring/expired states;
- expiry alerts.

### Duplicate/blacklist

- duplicate check on creation;
- blacklist status;
- blacklist reason categories;
- restricted blacklist reason visibility;
- review queue.

### Assignments

- partner companies;
- projects;
- worksites;
- positions;
- active assignment tracking.

### Advances & deductions

- record advances, deductions, additions with explicit entry-type / pay-effect fields (positive amounts);
- weekly (Thursday) summary by company and person;
- 20th-to-20th cycle report;
- deduction report and salary-deduction flag;
- search by person/company over a date range;
- restricted to office/HR/management roles.

### Equipment & issued items

- issue clothing/footwear/tools/medical with size and value;
- return tracking;
- cost recovery (deduction) for unreturned items;
- per-person retained history.

### Intake & profile

- intake fields: children, smoking, drinking, invalidity, tax bonus;
- payment method per person (cash / bank transfer);
- CV stored, printable, forwardable to the company.

### Coordinator tools

- mobile-friendly worker list;
- quick search;
- call/message shortcut;
- quick notes;
- assigned workers.

### Reports

- active workers by project/worksite;
- candidates by status;
- missing/expiring documents;
- pending approvals;
- weekly advance summary and 20–20 cycle report;
- equipment issued vs. returned;
- duplicate/blacklist review queue.

### Admin/security

- audit log;
- user management;
- basic settings;
- encrypted backup plan;
- 2FA for admin/HR/manager roles.

---

## 9.3 MVP should-not-have features

Do not include these in MVP unless CorvinumEU explicitly insists:

- accounting software integration;
- economic dashboard;
- profitability reports;
- accommodation management;
- payroll automation;
- advanced BI;
- AI document reading;
- worker self-service portal;
- offline mode;
- transportation route / vehicle / driver logistics (rejected in interview);
- automated SMS / email notification sending (rejected for MVP — calls + Messenger instead);
- worker self-service or feedback portal;
- daily shift / rota tables.

---

# 10. Phased roadmap

## Phase 0 – Discovery / blueprinting

Purpose:

- validate assumptions;
- confirm roles;
- confirm statuses;
- confirm required documents;
- confirm approval rules;
- confirm the advance/deduction ledger as in-scope and its exact rules (cycle, categories, who can enter/view);
- confirm equipment items, values, and deduction policy;
- confirm GDPR retention rules, including retained equipment-deduction and financial-ledger history;
- confirm MVP boundaries and the financial boundary (ledger yes, accounting no);
- produce implementation specification.

Outputs:

- finalized requirements;
- process map;
- data model;
- screen list;
- MVP backlog;
- technical architecture;
- project estimate.

---

## Phase 1 – Core HR registry and pipeline

Includes:

- login and roles;
- people registry;
- person profile;
- candidate pipeline;
- status lifecycle;
- basic search/filtering;
- recruiter/coordinator assignment;
- activity notes.

Outcome:

- CorvinumEU can stop relying on scattered spreadsheets for candidate/worker status.

---

## Phase 2 – Documents, approvals, compliance

Includes:

- document upload;
- document types;
- expiry dates;
- verification workflow;
- expiry alerts;
- activation checklist;
- approval screen;
- hard-stop activation rules.

Outcome:

- HR can control missing/expired document risk before someone becomes active.

---

## Phase 3 – Duplicate, blacklist, assignment, equipment & advances

Includes:

- duplicate detection;
- blacklist records;
- duplicate/blacklist review queue;
- partner companies;
- projects;
- worksites;
- positions;
- assignments;
- equipment / issued items with values and return tracking;
- advance & deduction ledger (explicit entry-type/pay-effect model, weekly + 20–20 summaries, search);
- coordinator mobile view (with equipment issuance).

Outcome:

- operational users can manage workers by real assignment context, recover equipment costs, and run the cash advance/deduction process with a reliable weekly summary and salary-deduction trail.

---

## Phase 4 – Reporting, GDPR, audit, polish

Includes:

- operational reports;
- export controls;
- audit log viewer;
- retention policies;
- anonymization workflow;
- backup monitoring;
- UX polish;
- staging/production workflow.

Outcome:

- management gets reliable operational visibility and the system becomes safer for real HR data.

---

## Later Phase / v2 ideas

- offline-capable PWA;
- multilingual SMS/message templates;
- worker portal;
- AI-assisted document parsing;
- document template generation;
- advanced analytics;
- external API integrations;
- accounting/payroll export, only if CorvinumEU later asks for it.

---

# 11. Pricing / offer structure logic

This section is not a final price. It is a structure for building the offer.

## 11.1 Recommended commercial structure

Use a staged offer instead of one giant fixed-scope monster.

Suggested structure:

1. **Discovery / Blueprinting fee**
2. **MVP build fee**
3. **Monthly hosting/support/maintenance fee**
4. **Optional feature expansion phases**

This protects both sides. CorvinumEU gets a clearer scope before paying for full development, and Syncmetric avoids building an infinite HR cathedral because someone remembered a dropdown in week six.

---

## 11.2 Discovery / Blueprinting package

Includes:

- stakeholder interviews;
- final questionnaire validation;
- workflow mapping;
- data model finalization;
- screen list;
- MVP backlog;
- implementation estimate;
- hosting/security plan.

Deliverables:

- written specification;
- process diagrams, optional;
- MVP backlog;
- fixed or phased quote.

Pricing logic:

- fixed one-time fee;
- credited partially or fully against MVP build only if desired commercially;
- useful as paid risk reduction.

---

## 11.3 MVP build package

Includes:

- implementation of approved MVP scope;
- staging environment;
- production environment;
- admin setup;
- basic training;
- go-live support.

Pricing logic:

- fixed project fee if scope is frozen;
- milestone-based payments;
- change requests billed separately.

Possible milestones:

1. Core registry and users
2. Pipeline/status workflow
3. Documents and approvals
4. Assignments and coordinator view
5. Reports/security/go-live

---

## 11.4 Monthly maintenance package

Includes:

- VPS/server hosting;
- backups;
- security updates;
- uptime monitoring;
- bug fixes within agreed SLA;
- small support requests;
- user/admin support.

Pricing logic:

- monthly retainer;
- separate tiers for basic/support-heavy clients;
- larger feature changes billed as new phase.

---

## 11.5 Optional feature packs

Possible add-ons:

- advanced reports;
- automated SMS / messaging templates (deferred per interview);
- payroll / accounting export, if later required;
- worker self-service portal;
- AI document OCR/import;
- multilingual document generation;
- offline PWA mode;
- payroll/accounting export if later required;
- advanced audit/GDPR package.

---

# 12. Technical architecture

CorvinumEU is **not** a greenfield build. It is derived from the existing Jober Django/htmx codebase (hardened, npm-free), which is roughly 60% of what CorvinumEU needs and whose Phase 4 (reporting, GDPR, audit, staging/production) is already complete. The shared HR core — people registry, pipeline, status lifecycle, documents, checklists, duplicate/blacklist (HMAC matching), RBAC, GDPR/retention, audit — is reused directly. CorvinumEU diverges by removing accommodation, transport logistics, and economic/P&L dashboards, and by adding the advance/deduction ledger and equipment cost recovery.

## 12.1 Stack (confirmed)

- Django (server-rendered) with htmx for interactivity; **npm-free** front end;
- PostgreSQL database;
- object storage for documents;
- Redis for queues/background work if needed;
- background worker (e.g. Celery/RQ or scheduled jobs) for expiry alerts, retention checks, and weekly advance summaries;
- role-based access control;
- encrypted backups;
- EU VPS hosting.

This matches the Jober production stack exactly, so the hardening, deployment, and backup tooling already built for Jober carry over. The CorvinumEU front end is themed to the corvinum.eu design system (see 7.0) — on the white-label model this theme is the per-client layer over the shared core.

## 12.2 Hosting model

Recommended:

- clean VPS controlled by Syncmetric or client-approved provider;
- EU region, preferably Slovakia/Germany/Austria/Czechia;
- staging and production environments;
- daily off-site backups;
- encrypted document storage;
- HTTPS with strict TLS;
- monitoring.

## 12.3 Security priorities

MVP security requirements:

- HTTPS only;
- secure cookies/sessions;
- 2FA for privileged users;
- RBAC permissions;
- audit logs;
- document access restrictions;
- backup encryption;
- server firewall;
- rate limiting on login;
- **no CDN runtime assets** — all external fonts, icons, scripts, and styles vendored locally and served by the app, with recorded provenance (source, licence, version, checksum) obtained via the asset-request process;
- least-privilege admin access.

## 12.4 Codebase strategy — shared-core platform (DECIDED)

**Decision:** one shared codebase, a reusable HR core, with each client as a thin layer of feature flags + branding + config. Jober and CorvinumEU are the first two clients of a white-label platform; future agencies are added the same way. Fork and long-lived branch are rejected (duplication, drift, and cherry-picking fixes across repos).

### Repo shape (one repo)

```
platform/
├── core/                    # client-agnostic platform spine
│   ├── accounts             # auth, users, roles, 2FA
│   ├── people               # person registry
│   ├── organizations        # partner companies / projects / worksites
│   ├── assignments          # person ↔ org/position
│   ├── workflow_history      # status transitions
│   ├── audit                # immutable audit log
│   ├── tasks                # action items / queues
│   ├── retention            # GDPR retention / anonymization
│   └── ui                   # shared templates/components, theme hooks
├── features/                # optional modules, switched on per client
│   ├── documents            # both clients (optional, but on)
│   ├── checklists           # both clients
│   ├── duplicate_blacklist  # both clients
│   ├── equipment            # CorvinumEU
│   ├── accommodation        # Jober
│   ├── profitability        # Jober (economic / P&L)
│   ├── worker_messaging     # Jober (Twilio SMS, Telegram)
│   └── advances             # CorvinumEU
├── clients/
│   ├── jober/               # settings · policies · workflows · templates · static
│   └── corvinum_eu/         # settings · policies · workflows · templates · static
└── deploy/
```

Note the boundary correction: **documents, checklists, and duplicate/blacklist are features, not core.** They are optional capabilities that both current clients happen to enable; the core stays the minimal client-agnostic spine.

### Feature flags (illustrative)

```python
# clients/corvinum_eu/settings.py
INSTALLED_APPS = [
    "core.accounts", "core.people", "core.organizations", "core.assignments",
    "core.workflow_history", "core.audit", "core.tasks", "core.retention", "core.ui",
    "features.documents", "features.checklists", "features.duplicate_blacklist",
    "features.equipment", "features.advances",
]
FEATURE_FLAGS = {
    "accommodation": False,
    "profitability": False,
    "worker_messaging": False,   # workers contacted by phone + Messenger
    "documents": True, "checklists": True, "duplicate_blacklist": True,
    "equipment": True, "advances": True,
}
CLIENT_POLICIES = "clients.corvinum_eu.policies"   # see client-policy interfaces below
```

### Build discipline (non-negotiable)

- the core never imports from a feature app; dependencies point feature → core only;
- the core contains **no client-specific conditional logic** (no `if client == "corvinum"`); client differences are expressed via feature apps, flags, theme, and config;
- core migrations run for every client; feature migrations run only where the feature is installed;
- per-client branding is config + CSS/template overrides, never business logic in the core;
- CI runs the full test suite under **each** client's flag set, so a core change that breaks any client is caught immediately.

### Client-policy interfaces (how the core stays client-agnostic)

The core never branches on client identity. Where clients legitimately differ — status sets, approval rules, who can do what, document requirements, workflow steps — the core defines an **interface** and calls it; each client supplies the implementation under `clients/<client>/policies` and `clients/<client>/workflows`. The core ships sensible defaults. This is the concrete mechanism behind the Stage D acceptance criteria (12.5): client difference lives in the client layer, not in `if client == ...` inside the core.

### Deployment

One versioned application artifact, deployed once per client. Each deployment gets:

- its own database;
- its own secrets;
- its own object storage;
- its own domain and TLS;
- its own backups;
- the **same versioned application artifact**;
- a selected client settings module (`clients/<client>/settings`).

GDPR isolation is therefore structural (separate database and storage per client), avoiding multi-tenancy complexity.

---

## 12.5 Build roadmap (Jober → shared core → CorvinumEU)

The plan moves in four stages. CorvinumEU specification work (this document) can proceed in parallel with finishing Jober.

### Stage A — Finish Jober first

- answer the remaining ~6 open Jober questions;
- complete Jober Phase 4 (reporting, GDPR, audit, staging/production);
- ship Jober to production; it becomes the reference implementation.
- *Status: Jober ~70% done, Phase 4 in progress. Timing depends on client responses.*

### Stage B — Extract the shared core from finished Jober

- audit every model/view/template and tag it **core HR** or **Jober-specific**;
- move core HR into `core/`; move Jober-only logic into `features/accommodation`, `features/financials`, `features/messaging`;
- remove any core→feature dependency; confirm all Jober tests pass under the new structure;
- extract shared templates/static/utilities (auth + 2FA, person profile, documents, HMAC duplicate matching, GDPR retention).
- *Rough effort: ~2–3 weeks, longer if the current code couples core to Jober-specific modules.*

### Stage C — Build CorvinumEU as the first thin client

- create `corvinum_eu/` settings: flags advances on, equipment on, accommodation/financials/messaging off;
- apply the corvinum.eu design system as the per-client theme (tokens lifted from the live CSS — see 7.0);
- build the two CorvinumEU feature apps: `features/advances` (advance & deduction ledger, weekly Thursday summary, 20–20 cycle) and `features/equipment` (issued items + cost recovery);
- where the reuse audit (7.0) clears them, reuse the corvinum.eu admin components (login, 2FA, password reset, applications inbox, bilingual CRUD); otherwise re-implement the design in our stack;
- deploy to staging, then production.
- *Rough effort: ~3–4 weeks features + ~1 week theming, given the spec is locked.*

### Stage D — Validate the platform (acceptance criteria)

- CorvinumEU ships with **no Corvinum-specific conditional business logic in the shared core** — client-specific behavior lives in feature apps, flags, theme, and config, never in `core/`;
- any change made to the core during the CorvinumEU build represents a **genuinely reusable platform capability**, not a one-client workaround;
- every core change **preserves Jober behavior**, proven by the Jober test suite passing unchanged;
- the full test suite passes under **both** Jober and CorvinumEU flag sets;
- a hypothetical third client is then config + branding + (optional) one feature app, not a rebuild.

The bar is not "the core never changes" — building the second client will legitimately surface reusable capabilities that belong in the core. The bar is that the core stays client-agnostic and that every core change is reusable and regression-free for Jober. That is the proof that turns "two clients" into a sellable platform.

---

## 12.6 Path to implementation-grade v0.6

This document is currently a **v0.6 working draft**. To reach implementation-grade v0.6, the following must be present and — where marked — confirmed with the client/team rather than drafted:

| v0.6 component | Status | Source / blocker |
|---|---|---|
| Confirmed status lifecycle | **Needs confirmation** | CorvinumEU has had one interview; statuses are proposed, not confirmed |
| Permission matrix (role × action) | Draftable now | Can produce a first matrix from roles in §4; confirm with client |
| Ledger state model | **Drafted (this version)** | Explicit-field model in 5.10 + data model; ledger rules (5.10) still need exact values |
| Document rules (mandatory docs, expiry) | **Needs confirmation** | Which documents are mandatory is a client question (13.2) |
| Feature matrix for both clients | Draftable now | Jober vs CorvinumEU on/off per feature — producible from known scope |
| Client-policy interfaces | **Drafted (this version)** | Mechanism defined in 12.4; concrete interfaces emerge during Stage B |
| Migration / extraction sequence | **Drafted (this version)** | Stages A–D in 12.5; per-app detail comes from the extraction matrix |
| Acceptance tests under both configs | Draftable now | Can draft the test outline; real tests written during build |

**Best next planning artifact:** a **Jober-to-platform extraction matrix** — every Jober app, model, view, template, command, and permission labelled *shared core / reusable optional feature / Jober client policy / Jober theme-UI / technical infrastructure / obsolete-removable*. That matrix makes the Stage B effort concrete and de-risks the extraction. It requires the Jober repository to complete.

---

# 13. Open decisions for the next back-and-forth

## 13.1 Product decisions

- Should the product be called HR CRM, PeopleOps, Workforce Management, or something client-friendly in Hungarian/Slovak?
- Should recruiters see only their own candidates forever, or only until activation?
- Should coordinators see full profiles or operational summaries only?
- Should observers be internal only, or can external partner companies have observer access later?
- Is test/work-trial handling definitely needed in MVP, or Phase 2?
- **Financial boundary: confirm the per-worker advance/deduction/travel ledger is acceptable as in-scope operational tracking, distinct from accounting/payroll.**
- Tax bonus (adóbónusz): store as information only, or compute? (Interview: the accountant currently handles it.)
- Should the child bonus be flagged/handled, given reluctance to pay it?
- Confirm which equipment items carry recorded values.

## 13.2 Data decisions

- Which identifier is legally and practically best for duplicate detection?
- Should the system store full identifier values, hashes, or both?
- Which documents are mandatory for CorvinumEU specifically?
- Which document types have expiry dates?
- What is the exact retention period for candidates who never become workers?
- What is the exact retention policy for blacklist/hash-only records?
- How long must advance/deduction ledger and equipment-deduction history be retained?
- Is bank account data stored for transfer-paid workers, and how is it protected?

## 13.3 Workflow decisions

- Who can approve Active Worker status?
- Who can propose blacklist?
- Who can approve blacklist?
- Who can remove blacklist?
- What happens when a person is a possible duplicate but not confirmed?
- Which checklist items should block activation?
- Who can enter and who can view advance/deduction entries?
- Should advances ever be capped/blocked, or always allowed?
- **Can an advance be partially recovered across cycles?** (Determines whether the ledger needs `recovered_amount`/linked recovery entries — see 5.10.)
- **Confirm the ledger rules in 5.10** (timezone + Thursday cut-off time, late-entry→Friday rule, cycle boundaries, correction vs reversal, immutability, export layout).
- Do worker complaints feed the blacklist automatically or via review?

## 13.4 UX decisions

- Interface language is **bilingual SK/HU** (confirmed by corvinum.eu and interview) — confirm SK or HU as the default.
- Default theme: follow corvinum.eu (light + dark toggle) — confirm which is default.
- Lift exact design tokens (colors, fonts, radius) from the live corvinum.eu CSS — confirm dev team access.
- Does CorvinumEU need mobile-first coordinator UX from day one?
- Should the new person wizard be short and fast, or detailed and strict?
- Should document upload happen during candidate creation or later?
- Should management dashboards be visible in MVP or kept as basic reports?

## 13.5 Commercial decisions

- Should Syncmetric propose discovery as a separate paid phase?
- Should MVP be fixed-price or phase/milestone-based?
- Should monthly support include small improvements or only maintenance?
- Should hosting be bundled into monthly maintenance?
- Should training be included in MVP or sold as onboarding support?

---

# 14. Immediate next design tasks

Recommended order for the next working sessions:

1. Review and simplify the status lifecycle.
2. Decide whether equipment/clothing management belongs in CorvinumEU scope.
3. Finalize the MVP must-have list.
4. Create a permission matrix.
5. Create first database schema draft.
6. Create first screen map / navigation structure.
7. Convert MVP into implementation backlog.
8. Convert backlog into proposal phases.
9. Draft client-facing offer text.

---

# 15. Current working assumptions

These assumptions should be confirmed before implementation.

1. CorvinumEU needs HR/personnel operations, not accounting automation.
2. The system will be used by internal staff only in MVP.
3. Workers will not log into the system in MVP.
4. Accommodation management is not needed (confirmed in interview).
5. Accounting/payroll software integration is not needed.
6. Economic / profit-and-loss dashboarding is not needed.
7. Equipment / clothing / tool / medical issuance with values and deductions IS needed (interview).
8. Transportation route/vehicle/driver logistics is NOT needed (rejected in interview).
9. Automated SMS/email notification is NOT needed for MVP — worker contact is by phone and Facebook Messenger.
10. A per-worker cash advance & deduction ledger IS needed (weekly Thursday summary, Friday cash, 20–20 cycle, salary deduction).
11. The advance/deduction ledger is operational cash tracking, pending client confirmation of the financial boundary.
12. Payment method varies per worker (cash or bank transfer).
13. CV is stored, printed, and forwarded to the partner company.
14. Intake captures children, smoking, drinking, invalidity, and tax-bonus details.
15. Duplicate and blacklist checking is important; worker complaints can feed placement/blacklist decisions.
16. Document expiry alerts are important; activation should require approval.
17. A worker belongs to one company/project (companies are the projects).
18. GDPR retention/anonymization, including retained financial and equipment-deduction history, needs legal confirmation.
19. The app's UI follows the existing corvinum.eu design system (bilingual SK/HU, light/dark, Material Symbols) and extends the admin panel already embedded in that site; exact tokens are lifted from its live CSS.

---

# 16. Back-and-forth notes

Use this section during discussion.

## Architecture decision (this session)

- White-label platform model adopted: one shared core, thin per-client layers (flags + branding + config).
- Fork and long-lived branch rejected.
- Build order: finish Jober → extract shared core → CorvinumEU as first thin client → platform ready for further clients.
- Separate instance + database per client; per-client theming (CorvinumEU = corvinum.eu design system).

## Decisions made (from first interview)

- No accommodation; no transport route/vehicle logistics; no automated SMS/email.
- Equipment/clothing/tools/medical issued with values; deduct cost if not returned.
- Cash advance & deduction ledger required: weekly Thursday summary, Friday cash distribution, 20th-to-20th cycle, deducted from salary. Modelled with explicit entry-type/pay-effect/settlement-status fields (positive amounts), not signed numbers.
- Payment method per worker: cash or bank transfer (some avoid bank accounts due to garnishments).
- CV stored, printed, forwarded to the company.
- Intake captures children, smoking, drinking, invalidity, tax bonus.
- Inactive statuses carry a reason (sick / quit / suspended / military) and a date; reactivatable leavers route back to the recruiter.
- A worker belongs to one company/project.
- Admin login should have a show-password toggle.

## Rejected ideas

- Transport routes / vehicles / drivers in the system (routes change constantly; drivers will not maintain them).
- Automated SMS/email to workers (they use phone calls and Facebook Messenger).
- Worker self-service / feedback portal.
- Daily shift / rota tables for workers.

## Questions for CorvinumEU

- Confirm the advance/deduction ledger is acceptable as in-scope (financial boundary).
- Tax bonus and child bonus: store only, or handle?
- Which equipment items carry recorded values?
- Retention periods for financial and equipment-deduction history.

## Questions for technical planning

- Encryption and access model for bank-account data and the financial ledger.
- How the weekly summary and 20–20 cycle report are generated and exported.
- Stack confirmed: Django/htmx (npm-free), derived from the existing Jober build. Codebase separation (fork vs. shared-core) pending the white-label decision — see 12.4.

## Proposal notes

- The advance/deduction ledger and equipment cost recovery are the real operational core for CorvinumEU and should anchor the demo.

---

# Addendum A1 — Fuel-money tracking (2026-07-05)

**Source & status:** relayed by the CorvinumEU **secretary** (secondhand,
2026-07-05), not the interview channel this document's decisions come from.
Recorded here so it steers Stage C planning, but **pending confirmation** with the
decision-maker before build. Do not treat as decided.

**Request:** track money spent on fuel, in two distinct cases —
1. **private cars** — money handed to workers who use their own car to get to
   work; and
2. **the bus** — fuel spend for company bus transportation.

## A1.1 Private-car fuel money → already designed (§5.10, `features/advances`)

This is the ledger's own worked example: one `PAY_ADDITION`, category
`travel_fuel`, `pay_effect = ADD`, positive amount — summarised in the Thursday
cycle and netted in the 20th-to-20th report like every other entry. **No new
module or model is needed.** The secretary's request *confirms* this planned
capability and sharpens it into a recurring commute-allowance use case.

New open decisions this raises (add to the §13.3 back-and-forth):
- **Calculation basis** — flat weekly/monthly amount per worker, per-km rate, or
  fuel receipts? (Model impact: none for flat/receipt amounts; a per-km rate
  would want `distance_km` + rate config on the entry.)
- **Cadence** — paid with the Friday cash distribution (existing flow), or
  monthly with the 20th-to-20th cycle?
- **Eligibility** — who approves that a worker qualifies as a private-car
  commuter (coordinator flag on the person? office decision?).

## A1.2 Bus fuel → NEW, small, and deliberately narrow (`features/fuel_costs`, tbd)

Bus fuel is a **company operational cost with no person and no payroll effect** —
it must **not** enter the per-worker ledger (every ledger entry has a person and
an explicit `pay_effect`; bus fuel has neither). Proposed shape, pending
confirmation:

- A minimal **fuel-spend log**: `date`, `vehicle_label` (free text or a tiny
  catalog — e.g. "Bus 1"; no fleet module), `amount` (positive Decimal, EUR),
  `odometer` (optional), `entered_by`, `note`. Reporting only: weekly/monthly
  totals, by vehicle label.
- **Boundary guards (both already decided in this document, and unchanged):**
  - This does **not** reopen transportation route/vehicle/driver logistics —
    rejected in the v0.4 interview and still rejected. No routes, no schedules,
    no driver assignments; just money spent on fuel.
  - This sits on the **financial boundary** (§3, 13.1): it is operational cost
    *tracking*, not P&L/accounting. Like the ledger, it needs explicit client
    sign-off as in-scope operational tracking. If CorvinumEU actually wants
    cost-vs-revenue analysis around it, that is the (excluded) profitability
    scope and must be renegotiated, not slipped in.

Open decisions to confirm: single "bus" bucket vs per-vehicle labels; receipts
kept (photo upload → touches the documents feature) or amount-only; who enters
it (office/coordinator); does spend need partner-company/project attribution.

## A1.3 Stage C impact

- `features/advances` scope is unchanged (private-car money was already in it);
  the A1.1 open decisions join the pre-build ledger-rules checklist (§5.10).
- `features/fuel_costs` is a candidate **new, CorvinumEU-only feature app** —
  small (one model, one form, one report). Not shared with Jober (Jober tracks
  transport as weekly headcounts and fuel as a finance line item, which stays in
  `features/profitability`).
- Neither item changes the Stage B extraction plan; both are Stage C build items
  once confirmed.
