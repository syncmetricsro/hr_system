# Build Journal

## 2026-06-13

Built the v1 static HR operations demo inside `demo/`.

What changed:
- Added `demo/index.html`, `demo/styles.css`, and `demo/app.js`.
- Implemented the CorvinumEU default theme and live Jober theme switch with CSS custom properties.
- Implemented the global top bar, role switch, client switch, sidebar, guided manifest rail, and decision capture panel.
- Implemented the full guided sequence: sign in, dashboard, staffing decision, blacklist risk check, work test approval, shift and transport decision, fake SMS, second shift, sick leave, certificate hard-stop, mobile manager view, and Jober module reveal.
- Added Jober-only Accommodation, Equipment, and Pohoda dashboard screens.
- Kept all demo state in plain in-memory JavaScript. No persistence APIs, backend, dependencies, remote scripts, remote styles, or media assets were added.

Design decisions:
- Followed the local `demo/frontend-design/SKILL.md` direction by grounding the interface in workforce logistics: manifests, rosters, risk gates, shifts, buses, and document stops.
- Used the manifest rail as the single aesthetic risk. It works as both guided stepper and operational route strip, so the memorable visual device carries product meaning instead of decoration.
- Used the approved token palettes from the plan for CorvinumEU and Jober.
- Used Option A typography: system stacks that prefer Michroma, Noto Sans, and JetBrains Mono only when already present on the machine.
- Self-critique outcome: removed the narrow-layout promotion of the manifest rail after screenshot review because it hid the active screen on mobile. The mobile layout now places the active screen first.

Deferred:
- No real media assets or font files. Option B self-hosted fonts can be added only if the human delivers the files and licenses.
- No real SMS, authentication, database, or Pohoda connection.

Next step:
- Review the demo in a normal browser window before the meeting and tune copy or screen density if the presenter wants a different walkthrough rhythm.

## 2026-06-13

Responsive retrofit and spec filename fix.

What changed:
- Renamed `demo/demo_prototype_build_specs.md` to the canonical `demo/demo_prototype_build_spec.md` so the file on disk matches `AGENTS.md` / `CLAUDE.md` references.
- Retrofitted the shell for tablet and phone without rebuilding the demo: desktop keeps the three-column layout above 1024px.
- Added a hamburger drawer for tablet/phone navigation and moved mobile Client / Role controls into that drawer.
- Converted the right Live manifest rail into a collapsible top progress strip below 1024px, with all 12 stops reachable.
- Restacked dense tables into labelled cards at phone width.
- Made decision cards stack vertically on phone.
- Made the manager field view read as a phone-native screen at phone width rather than a desktop page containing a heavy phone mockup.
- Added spacing and tap-target CSS tokens so controls have more consistent gaps and phone buttons are easier to hit.
- Added isolated Playwright test tooling at the repo root, outside `demo/`, using the pinned Docker workflow.

Decisions made:
- Used a hamburger drawer instead of bottom tabs because Jober adds too many nav items for a reliable thumb tab bar.
- Used 1024px as the shell breakpoint and 640px as the phone/card breakpoint.
- Kept the manifest as the signature element by adapting it to a mobile progress strip instead of hiding it.
- Used Playwright, not Puppeteer, because repo policy defines a specific Playwright-in-Docker workflow.

Deferred:
- No new media, fonts, framework, runtime dependency, backend, or production scaffold.

Next step:
- Review the responsive demo manually on the actual presentation phone and laptop for meeting-specific pacing and density.

## 2026-06-13

Desktop spacing and tap-target cleanup.

What changed:
- Tightened the shared spacing system in `demo/styles.css` with reusable control, action-row, and stack-gap tokens.
- Increased shared buttons and segmented switch buttons to a 44px minimum hit target.
- Added consistent separation after form grids, status badges, alert/callout blocks, message boxes, and action rows so buttons no longer sit flush against nearby content.
- Increased decision-card padding/gaps and form-field gutters to keep dense screens readable without changing the desktop shell.
- Added a Playwright regression check that verifies visible button height and control spacing across the desktop walkthrough screens.

Decisions made:
- Fixed the issue at the component spacing layer instead of tuning each screen separately, because the cramped controls came from repeated action-row and callout patterns.
- Kept the existing desktop information architecture and responsive breakpoints intact.

Next step:
- Review the updated pages on the presentation laptop to confirm the spacing matches the desired meeting-room density.

## 2026-06-13

Split the demo into internal, CorvinumEU-only, and Jober-only builds.

What changed:
- Moved the existing combined demo unchanged into `demo/internal/`.
- Created `demo/corvinum/` as a CorvinumEU-only static build with its own `index.html`, `styles.css`, and `app.js`.
- Created `demo/jober/` as a Jober-only static build with its own `index.html`, `styles.css`, and `app.js`.
- Removed the client switch from both client-facing builds.
- Removed all Jober-only strings/modules/data from the CorvinumEU build source.
- Removed all CorvinumEU references from the Jober build source.
- Gave Jober a different primary IA: folder-style tabs for Operations, People, Compliance, Logistics, Accounting, and Reports; nested sections live under each folder.
- Replaced Jober's right-side manifest rail with a slim numbered step bar under the folder tabs.
- Made Accommodation, Equipment, and Pohoda normal Jober tabs rather than licensed extras.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, `deployment_journal.md`, and the Playwright suite for the three-build structure.

Decisions made:
- Kept CorvinumEU close to the original operational rail/sidebar layout because that is the requested client-facing shape.
- Treated Demand as an Operations sub-section in Jober because the guided story needs the staffing decision before dispatch planning.
- Kept the internal build as the only place where the platform/resale client switch is visible.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 8 tests across phone, tablet, and desktop.
- Visual screenshots were reviewed for CorvinumEU and Jober at desktop and 375px.

Next step:
- Open the two client builds on the actual meeting laptop/phone and decide whether Jober's Demand sub-section should stay under Operations or move elsewhere.

## 2026-06-13

Added English, Slovak, and Hungarian language switching to all demo builds.

What changed:
- Added an in-memory EN / SK / HU language switch to `demo/internal/`, `demo/corvinum/`, and `demo/jober/`.
- Wired the switch through primary navigation, role labels, guided controls, decision labels, page headings, table headers, and status badges.
- Kept the language choice intentionally non-persistent; it resets on reload like the other demo state.
- Kept the Jober folder-tab grouping data-driven while translating labels at render time.
- Updated `AGENTS.md`, `demo/demo_prototype_build_spec.md`, and the Playwright suite to cover language switching.

Decisions made:
- Mock names, company names, phone numbers, dates, and most audit/demo data remain fixed source data for now; the language layer focuses on the UI and presentation surface.
- CorvinumEU keeps the language switch inside the mobile drawer, alongside Role. Jober shows Role and Language directly in the mobile top area because it has no drawer.

Verification:
- `grep -ri jober demo/corvinum/` returned no output.
- `grep -ri corvinum demo/jober/` returned no output.
- The pinned Docker Playwright suite passed with 9 tests, including language switching in all three builds.

Next step:
- Review Slovak and Hungarian wording with a fluent speaker before client presentation if exact business terminology matters.
