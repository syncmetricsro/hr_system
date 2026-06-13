# Demo Prototype — Build Spec

**For:** Claude Code (build target)
**Project:** HR operations platform — internal and client-facing clickable demos
**Type:** Static, clickable HTML prototype. No backend, no real data, no build step.
**Source of truth for product logic:** `shared_hr_platform_architecture.md` (v0.3). This spec covers only the demo.

---

## 1. What this is and why it exists

A clickable front-end mockup used in a live client meeting. It is **not** production software and must not pretend to be — no real auth, database, SMS, or Pohoda connection.

It has two jobs, equally important:

1. **Sell the vision** — walk a non-technical client through one worker's journey end to end so the product becomes tangible.
2. **Extract decisions** — the client has been hard to get answers from in writing. Several open questions are built into the demo as on-screen A/B choices, so the client decides by clicking rather than by answering an email. The prototype records which option they picked (in memory) so the choices can be reviewed after the meeting.

Build everything in service of those two jobs. When in doubt, favour clarity and "showability" over completeness.

---

## 2. Build outputs and audience separation

The demo now ships as three static builds:

- `demo/internal/` — internal combined build. This keeps the original live CorvinumEU/Jober switch for internal platform/resale explanation.
- `demo/corvinum/` — CorvinumEU-only client build. This keeps the green/steel sidebar + Live manifest rail layout and contains only core HR operations modules.
- `demo/jober/` — Jober-only client build. This uses Jober's folder-tab "fülek" navigation and includes Logistics and Accounting modules as normal product areas.

Client-facing builds are not skins with hidden feature flags. They are source-level separations:

- `demo/corvinum/` must contain no Jober strings, data, modules, logos, or palette anywhere in HTML/CSS/JS.
- `demo/jober/` must contain no CorvinumEU references anywhere in HTML/CSS/JS.
- Verify before release with `grep -ri jober demo/corvinum/` and `grep -ri corvinum demo/jober/`; both commands must return no output.

---

## 3. Technical constraints

- **Build location:** create all prototype files inside `HR_System/demo/`. The runnable builds live in `demo/internal/`, `demo/corvinum/`, and `demo/jober/`. Leave the rest of `HR_System/` empty — do **not** scaffold the future product structure (`src/`, `modules/`, `clients/`) yet.
- **Plain static web app.** Vanilla JS, HTML, CSS. No framework, no bundler, no npm build. Must run by opening `HR_System/demo/index.html` directly or via a trivial static server.
- **Suggested file layout** for each build folder: `index.html`, `app.js` (views + router + mock data + state), `styles.css`.
- **No persistence APIs.** Hold all state in plain JS variables/objects in memory. Do **not** use localStorage/sessionStorage. State resets on reload — that's fine and expected for a demo.
- **View routing:** simple JS show/hide of view containers, or hash-based routing (`#/people`, `#/profile/olha`). Either is fine; keep navigation obviously clickable.
- **UTF-8 throughout.** The mock data deliberately includes Cyrillic and Central-Asian names (see §7); they must render correctly. This doubles as a visible demonstration of the multi-script requirement.
- **Languages:** every build supports English, Slovak, and Hungarian through an in-memory language switch. Do not call translation APIs, load remote language packs, or persist the selected language.
- **Responsive:** desktop-first for admin views; include one mobile-framed view for the manager's field screen (§6, screen 11). Test the client-facing builds at phone, tablet, and desktop widths.
- **Quality floor:** visible keyboard focus, sensible contrast, `prefers-reduced-motion` respected.

### 3.1 Responsive behavior

The demo must work for live presentation on a computer and on mobile phones.

- **Desktop, above ~1024px:** internal and CorvinumEU keep the three-column shell: left nav, main content, and right Live manifest rail. Jober uses top folder tabs and no right rail.
- **Tablet, ~641-1024px:** internal and CorvinumEU collapse the left nav into a hamburger drawer; convert the Live manifest rail into a collapsible top progress strip; content uses the full width. Jober keeps folder tabs at the top and uses a slim numbered step bar under them.
- **Phone, <=640px:** use a single-column layout; dense tables restack into labelled cards; decision A/B cards stack; the manager field view reads as a phone-native screen.
- The Live manifest must never disappear in internal/CorvinumEU. On mobile and tablet it shows the current stop and expands on tap to reveal all stops.
- Jober's guided progress is a slim numbered step bar under the folder tabs, with Back/Next controls.
- Guided-demo Back/Next, Role switch, and decisions panel must remain reachable and touch-friendly. The Client switch exists only in `demo/internal/`.
- Controls should have consistent group spacing, edge padding, and a minimum tap target around 44px.
- No horizontal scrolling, clipped controls, or overlap at 375px, 768px, or wide desktop widths.

---

## 4. Design direction

Read the `frontend-design` skill before building and produce a small token system (palette, type, layout, signature) first. Direction notes specific to this brief:

- **Ground it in the subject:** this is workforce logistics — people, shifts, worksites, buses, documents, risk gates. The interface world is dispatch boards, rosters, status, and time. Lean into that operational character. Avoid the generic SaaS-dashboard default (cream + serif + terracotta, or black + acid-accent). Pick a direction that reads as a serious operational tool people use all day.
- **Three presentation surfaces.** The internal build demonstrates the shared-platform switch. The client builds must look and behave as independent products:
  - CorvinumEU — green/steel operational rail, left sidebar, right Live manifest.
  - Jober — cobalt/teal/magenta folder-tab system, grouped sections, no sidebar or right rail.
- **Status is the core visual language.** The two status dimensions (hire status and availability) appear constantly. Give each a clear, consistent badge treatment. Hire status: Recruit / Hired / Archived / Blacklisted. Availability: Working / Available / Inactive. These must be instantly legible.
- **Copy:** plain, active-voice, sentence case. Buttons say what happens ("Approve hire", "Assign to shift", "Send pickup notice"). Name things from the user's side. See the writing guidance in the skill.

---

## 5. Global chrome

Present on every screen:

- **Top bar:** wordmark · **Role switch** control (Recruiter / Manager / Observer) · **Language switch** control (EN / SK / HU) · user avatar. The Client switch appears only in `demo/internal/`.
- **Role switch behaviour:**
  - *Recruiter* — can create people, schedule tests, assign shifts/transport, upload docs. Cannot approve hires or blacklist.
  - *Manager* — everything, including approvals, demotion, blacklist, verification.
  - *Observer* — read-only. All action buttons hidden or visibly disabled. Use this to demonstrate the permission model in one click.
- **CorvinumEU nav:** left sidebar with People · Staffing requests · Shifts & transport · Documents · Approvals · Reports.
- **Jober nav:** top folder-style tabs:
  Operations (Dashboard, Demand, Shifts, SMS pickup, Second shift, Field mode) · People (Roster scan, Approvals) · Compliance (Documents, Sick leave) · Logistics (Accommodation, Equipment) · Accounting (Pohoda) · Reports.
- **Guided tour control:** a "Start guided demo" button and unobtrusive Next/Back stepper that walks the §6 narrative in order. The presenter can also free-click. When a decision screen is reached, the tour pauses on it.

---

## 6. The primary click path (the demo narrative)

Build these as the guided sequence. Each step is a screen or an action with a clear next step.

**1 — Login.** Branded login with email + password and a 2FA note for privileged roles. A single "Sign in" advances to the dashboard. (Cosmetic; no real auth.)

**2 — Manager dashboard.** Today's picture: count working now, documents expiring soon, blacklist review queue, pending hire approvals. Each tile links to its screen.

**3 — Staffing request (DECISION 1 — demand side).** A partner company needs 12 workers at Worksite A next Tuesday. Present the open question on screen as two paths:
   - **Option A — Order-driven:** the partner's request exists as an order record that recruiters fill by assigning workers to shifts.
   - **Option B — Shift-driven:** recruiters create shifts directly; there is no order object.
   Let the presenter pick. Record the choice. Whichever is picked, continue into the shift flow. Label this clearly as "Help us confirm how you actually work."

**4 — Create candidate + live risk check.** Recruiter opens "Add person" and enters a name/identifier. As they type, a live duplicate/blacklist check runs. For the seeded blacklisted returnee (see §7), it fires a **strong blacklist warning** and blocks activation pending manager review. This is the headline moment — make the catch feel decisive but not alarming. Allow saving as Recruit with the flag attached; activation is gated.

**5 — Work test + approval.** Recruiter schedules a work test for a clean candidate, fills a short recommendation form (a few fields + recommend/don't recommend). Switch to Manager role → **Approve hire**. Candidate's hire status flips **Recruit → Hired**. Show the audit entry being written.

**6 — Assign to shift + transport (DECISION 2 — transport capacity).** Assign the now-Hired worker to a shift: worksite, position, date/time, and a **transport group** (a specific bus + pickup point + time). When the bus is near capacity, present the open question:
   - **Option A — Enforce capacity:** block assignment when the bus is full.
   - **Option B — Record only:** allow it, just record it.
   Record the choice. Show both status dimensions in the worker's header: hire = Hired, availability = Working.

**7 — SMS pickup notice.** Show the pickup SMS composed and ready ("Bus 2, 06:15, Nitra depot…") with a **Send pickup notice** button that shows a "Sent" confirmation — but nothing is actually sent. Make clear this is the SMS channel (primary, since many workers lack email).

**8 — Second shift, same day.** Add a second shift later the same day at a *different* worksite with a *different* transport group. This is the moment the shift model's purpose lands: one worker, multiple dated shifts, transport that varies by worksite.

**9 — Sick leave → auto-inactive.** Record a sick-leave entry (dates only — no medical detail, state this explicitly on screen). Availability auto-flips to **Inactive** and the shifts inside the window show as cancelled. Reinforces the dates-only, GDPR-light approach.

**10 — Certification expiry hard-stop (DECISION 3 — cert storage).** A worker's forklift certificate is expiring in ~12 days; show the alert. Try to assign them to a Forklift-operator position → the system **hard-stops** it (required cert invalid). At the cert record, present the open question:
   - **Option A — Store the file:** upload and keep the certificate document.
   - **Option B — Dates only:** store type + expiry, no file.
   Record the choice.

**11 — Manager field view (mobile).** A narrow, phone-framed view: today's workers, quick search, status + document state at a glance, call / message shortcuts, "mark no-show". Demonstrates the mobile-first manager (= coordinator) use.

**12 — Internal-only Jober reveal.** In `demo/internal/`, flip the **Client switch** to Jober. The app re-skins and three nav items appear: **Accommodation**, **Equipment**, **Pohoda dashboard**. Client-facing builds do not include this reveal step: CorvinumEU stops after the manager field view, while Jober exposes those modules as normal tabs from the start.

---

## 7. Mock data set

Seed a small, coherent dataset so the narrative holds together. Names intentionally span scripts to demonstrate i18n.

**People (roster):**
- **Olha Tkachenko** — Hired, Working. Ukrainian. The worker used in steps 6–9 (shifts, SMS, sick leave).
- **Bohdan Marchenko** — Blacklisted (category: repeated no-show). The returnee caught in step 4.
- **Farrukh Yusupov** — Hired, Available. Holds a forklift certificate expiring in 12 days (step 10).
- **Tran Van Minh** — Recruit, test scheduled (a clean candidate for step 5).
- A few extra rows (mixed statuses) to make lists look real.

**Partner company:** "Stavby Nitra s.r.o." (construction/logistics partner) — needs 12 workers (step 3).

**Worksites:** Worksite A — Nitra warehouse; Worksite B — Trnava site.

**Positions:** General laborer; Warehouse picker; **Forklift operator** (requires valid forklift certificate).

**Buses:** Bus 1 (capacity 15); Bus 2 (capacity 9, used for the near-capacity moment in step 6). Each with a named driver and a pickup point/time.

**Documents/certs:** at least one expiring document and Farrukh's expiring forklift cert, to populate the dashboard alerts.

Keep all of this in one mock-data object in `app.js`.

---

## 8. Jober screens

In `demo/internal/`, these are revealed by the client switch. In `demo/jober/`, these are normal folder-tab sections under Logistics and Accounting:

- **Accommodation:** a simple room list with occupancy (e.g. Room 12 — 3/4 beds), and a worker → room assignment. No costs.
- **Equipment:** issued gear per worker with status (issued / returned), and a **sizes** panel on the worker (shirt / trousers / boots) feeding inventory.
- **Pohoda dashboard:** a mocked read-only dashboard with placeholder figures and a clearly visible "Demo data — connected via Pohoda mServer (XML)" label. Do **not** attempt any real connection.

These three never appear in `demo/corvinum/`, including in source.

> **Note for the future build (not part of this demo).** When the real application is built, it grows inside the same `HR_System/` folder as one codebase: `src/` (shared core), `modules/` (feature modules toggled by flags — accommodation, equipment, pohoda-dashboard…), and `clients/` (per-client **config + theme only**, no business logic). The demo's client switch is the runtime preview of exactly that idea: one app, swap the config, get a different client. Do not build this structure now — it's recorded here only so the demo and the eventual build stay aligned.

---

## 9. Decision capture

The three DECISION screens (§6 steps 3, 6, 10) each record the presenter's pick in an in-memory object. Add a small **"Decisions captured"** panel (reachable from the top bar) that lists the three questions and the option chosen for each, so the team can review them straight after the meeting. Resets on reload — that's acceptable; the presenter notes them down.

### 9.1 Language support

All three builds include English, Slovak, and Hungarian UI labels. The language switch is demo-only in-memory state, like the role and decision state. It is intentionally not persisted, and it must not use any remote translation service.

The language layer should keep navigation, guided controls, role labels, decision labels, page headings, table headers, mobile card labels, status badges, callout prose, audit lines, and client-module labels translatable in the client-facing builds. Mock names, company names, phone numbers, and fixed dates may remain unchanged demo data.

---

## 10. Explicitly faked or out of scope

Show as "this is where X lives", do not build:

- Real authentication, real database, real persistence.
- Real SMS sending (compose + fake "Sent" only).
- Real Pohoda connection (mocked dashboard only).
- Route planning / optimisation (future upsell — omit).
- Worker self-service portal (Phase 2 upsell — omit).
- Automated medical-document scanning (future upsell — omit).

---

## 11. Definition of done

- Lives entirely in `HR_System/demo/`, with the rest of `HR_System/` left empty.
- Loads with no console errors by opening or serving `HR_System/demo/internal/index.html`, `HR_System/demo/corvinum/index.html`, and `HR_System/demo/jober/index.html`.
- The full §6 guided sequence runs start to finish via the stepper, and every screen is also reachable by free-clicking the nav.
- The internal Client switch re-skins the internal app and toggles the Jober-only nav items live.
- The CorvinumEU client build contains no Jober source strings or modules; the Jober client build contains no CorvinumEU source strings.
- The Jober client build uses folder tabs as the primary navigation and exposes Accommodation, Equipment, and Pohoda as normal tabs.
- English, Slovak, and Hungarian can be selected in all three builds without persistence or remote services.
- Role switch visibly changes what an Observer can do versus a Manager.
- The three decision screens record and display the chosen options.
- Cyrillic and Central-Asian names render correctly throughout.
- Both status dimensions are visible and consistent wherever a person appears.
