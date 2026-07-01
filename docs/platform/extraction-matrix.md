> **Status: FUTURE-STAGE PLANNING — does not change the current build.**
> Per [ADR 0001](../adr/0001-jober-only-scope.md) the production app stays
> **single-client Jober** with no platform abstractions, client switching, or
> shared-client data models. This matrix is a **post-completion** extraction
> checklist (Stage B; see [ADR 0020](../adr/0020-white-label-platform-sequencing.md)).
> It is a DRAFT seeded from design-level entities and **must be completed against
> the actual Jober repository** before any extraction begins. Nothing here
> authorises platform work in the current codebase.

# Jober → Platform Extraction Matrix

**Purpose:** label every Jober artifact so the shared-core extraction (Stage B, design doc §12.5) is a checklist, not a guess.
**Status:** DRAFT — seeded from design-level entities only. **Must be completed against the actual Jober repository**, enumerating real apps, models, views, templates, management commands, and permissions.

---

## Labels

| Label | Meaning | Target location |
|---|---|---|
| **core** | Client-agnostic platform spine; both/all clients need it | `core/*` |
| **feature** | Reusable optional module, switched on per client | `features/*` |
| **client-policy** | Jober-specific business rule (statuses, approvals, workflows) | `clients/jober/policies` · `clients/jober/workflows` |
| **theme-ui** | Jober-specific branding, templates, static | `clients/jober/templates` · `clients/jober/static` |
| **infra** | Technical infrastructure (deploy, CI, settings, utilities) | `deploy/`, shared config |
| **obsolete** | Dead, superseded, or removable | delete |

**Assignment rule:** default a thing to the *most client-agnostic* label it can honestly hold. If it contains an `if client/feature`-style branch, split it: the agnostic part → core, the specific part → client-policy or feature. "Already in Jober" never auto-labels as core (see design doc §7.0 reuse audit).

---

## How to complete

For **every** Jober app, then within each: every model, view/route, template, management command, signal/task, and permission/group — add a row. Aim for one row per real artifact, not per concept.

Columns: **Artifact · Type · Current Jober location · Label · Target location · Depends on · Notes / split required**

---

## Seed rows (design-level entities — verify and expand against the repo)

| Artifact | Type | Label | Target | Notes |
|---|---|---|---|---|
| User, Role, Permission, 2FA | model/auth | core | `core/accounts` | confirm Jober auth maps cleanly to platform RBAC |
| Person, PersonIdentifier | model | core | `core/people` | identifiers encrypted; access audited |
| PartnerCompany, Project, Worksite, Position | model | core | `core/organizations` | "companies are projects" per CorvinumEU interview |
| Assignment | model | core | `core/assignments` | one worker → one org/project |
| StatusHistory | model | core | `core/workflow_history` | transitions only; allowed transitions are client-policy |
| AuditLog | model | core | `core/audit` | immutable |
| Task, Notification | model | core | `core/tasks` | internal notifications (not worker messaging) |
| RetentionPolicy | model | core | `core/retention` | GDPR; per-client retention values are config |
| Shared templates / base layout / components | template | core | `core/ui` | theme hooks; no client branding baked in |
| Document, DocumentType | model | feature | `features/documents` | on for both clients |
| ChecklistTemplate, ChecklistItemTemplate, PersonChecklistItem | model | feature | `features/checklists` | on for both clients |
| DuplicateMatch, BlacklistRecord | model | feature | `features/duplicate_blacklist` | HMAC matching; on for both |
| IssuedItem (equipment) | model | feature | `features/equipment` | CorvinumEU on; Jober likely on (coordinator handles equipment) |
| LedgerEntry (advances/deductions) | model | feature | `features/advances` | CorvinumEU; **check overlap with Jober financials** |
| Accommodation models | model | feature | `features/accommodation` | Jober only |
| Economic / P&L dashboards | model/view | feature | `features/profitability` | Jober only |
| SMS (Twilio), Telegram messaging | model/integration | feature | `features/worker_messaging` | Jober only; CorvinumEU off |
| TestEvent / ScreeningEvent | model | feature | `features/recruitment` (tbd) | optional; confirm whether core or feature |
| ActivityNote | model | core | `core/people` | person timeline |
| Status set + allowed transitions (Jober's specific values) | logic | client-policy | `clients/jober/policies` | the *values*; the *mechanism* is core |
| Activation/approval rules (Jober thresholds) | logic | client-policy | `clients/jober/workflows` | hard-stops differ per client |
| Jober branding, colours, logo, templates | static/template | theme-ui | `clients/jober/*` | CorvinumEU mirror = corvinum.eu design system |
| Settings, deploy scripts, CI config | config | infra | `deploy/`, shared | per-client settings module selected at startup |

---

## Open flags surfaced by this matrix

- **Advances vs. Jober financials overlap.** If Jober's financial code already handles per-worker money movement, `features/advances` may reuse it rather than be net-new — this changes the CorvinumEU effort estimate. Resolve early.
- **Equipment on both clients.** If Jober also issues equipment, `features/equipment` is a shared feature, not CorvinumEU-only.
- **Auth compatibility.** Confirm Jober's auth/2FA maps onto the platform RBAC before labelling `core/accounts` as clean reuse (design doc §7.0).
- **Anything labelled core that imports a feature** must be split before extraction — that coupling is the main risk to the Stage B estimate.
