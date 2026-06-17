# AGENTS.md — HR_System

Instructions for any coding agent working in this repository. These rules are binding. If a rule here conflicts with a task, follow the rule and say why.

This file is agent-agnostic. The detailed product and build requirements live in **`demo_prototype_build_spec.md`** — read it before building. This file governs scope, security, and how to work; the spec governs what to build.

---

## Project state

- The only thing to build right now is the **demo prototype**, in `HR_System/demo/`.
- The demo is **static vanilla HTML, CSS, and JavaScript**. It has **no backend and no dependencies**, by design.
- A production application will later live in the same `HR_System/` folder. Its package rules are in "Phase 2" below. **Do not scaffold or build it yet.** Do not create `src/`, `modules/`, or `clients/` now.

---

## Current task — build the demo

Build into `HR_System/demo/`. Follow `demo_prototype_build_spec.md` for the full spec. In brief, the deliverable is a clickable, presenter-driven prototype split into three static builds:

- `demo/internal/` — the internal combined demo with the live CorvinumEU/Jober switch.
- `demo/corvinum/` — the CorvinumEU-only client build.
- `demo/jober/` — the Jober-only client build.

The client builds must be true source-level separations, not runtime hiding:

- `demo/corvinum/` must contain no Jober strings, data, modules, logos, or palette in HTML/CSS/JS.
- `demo/jober/` must contain no CorvinumEU references in HTML/CSS/JS.
- Verify with `grep -ri jober demo/corvinum/` and `grep -ri corvinum demo/jober/`; both must return no output.

The demos:

- walks one worker's journey end to end (create → risk check → work test → hire approval → shift + transport → SMS notice → second shift → sick leave → certification hard-stop → manager mobile view); the internal build also keeps the "become Jober" finale;
- keep the live two-client switch only in `demo/internal/`; remove the client switch entirely from both client-facing builds;
- ship CorvinumEU as a sidebar + manifest-rail HR operations build;
- ship Jober as a folder-tab build with Operations, People, Compliance, Logistics, Accounting, and Reports tabs;
- has a **role switch** (Recruiter / Manager / Coordinator / Observer) that changes what actions and screens are available, with Observer read-only;
- has an in-memory **language switch** for English, Slovak, and Hungarian in every build. Do not use remote translation services or persistence; language resets on reload.
- keeps the demand-model question as the only open on-screen A/B choice, while the decision panel marks Transport capacity = Enforce and Certificate storage = Dates only / metadata only as already answered;
- uses mock data containing Cyrillic and Central-Asian names that must render correctly (this also demonstrates the multi-script requirement).

Role boundaries:

- **Recruiter** can create people, schedule tests, assign shifts/transport, send pickup notices, and update document metadata. Recruiter cannot approve hires, blacklist, demote, or verify certifications.
- **Manager** can approve hires, blacklist/demote, verify certifications, and use HR/approval screens.
- **Coordinator** is a distinct logistics role, not a Manager alias. In CorvinumEU, Coordinator sees transport logistics only. In Jober, Coordinator sees transport, accommodation, and equipment logistics. Coordinator screens must contain only logistics-relevant data: worker name, assigned worksite, transport group, shift dates, plus room/equipment issued in Jober. Coordinator must not see hire status, documents, certifications, screening/work-test results, approval history, or blacklist status; HR/approval screens must not be reachable and their data must be absent from the DOM.
- **Observer** is read-only. Action buttons are disabled or hidden.
- Permissions are role-based only; do not add per-person permission editing.

Confirmed product decisions:

- The product is shifts-first for assignment: once a worker is Hired, the worker is directly shift-eligible. Do not imply a contract/signing step before shifts.
- Transport capacity is enforced per vehicle. A full vehicle blocks new assignments.
- Certificate records are metadata only: type, issue date, expiry date, and valid/invalid status. No certificate file upload or retention.

### Technical constraints (demo)

- Plain **vanilla HTML/CSS/JS**. No framework, bundler, transpiler, or build step.
- Suggested layout in `HR_System/demo/`: `index.html`, `app.js`, `styles.css`. A single self-contained `index.html` is also acceptable.
- **No persistence APIs.** Hold all state in plain in-memory JS. Do **not** use `localStorage` / `sessionStorage`. State resets on reload — that is intended.
- **UTF-8 throughout.**
- Quality floor: visible keyboard focus, sensible contrast, `prefers-reduced-motion` respected; one mobile-framed view for the manager field screen.

### Responsive behavior (demo)

- The demo is presented on desktop computers, tablets, and phones. It must have no horizontal scrolling, clipping, or overlapping controls at `375px`, `768px`, and wide desktop widths.
- Above `1024px`, the internal and CorvinumEU builds keep the desktop three-column shell: left nav, main content, and right Live manifest rail. The Jober build uses top folder-style tabs and no right rail.
- From `641px` to `1024px`, internal and CorvinumEU collapse navigation into a reachable hamburger drawer, convert the Live manifest rail into a top progress strip, and let content use the full width. Jober keeps folder tabs at the top and uses a slim numbered step bar under them.
- At `640px` and below, use a phone layout: dense tables become stacked labelled cards, decision A/B cards stack vertically, and the manager field view reads as a native phone screen rather than a shrunken desktop surface.
- The Live manifest is the internal/CorvinumEU signature element and must remain available on mobile as an expandable progress strip. Jober's signature navigation is the folder-tab "ears" plus numbered step bar.
- Guided Back/Next controls, Role switch, and decisions panel must remain usable at every responsive width. The Client switch exists only in `demo/internal/`.
- Touch controls should have a minimum target around `44px`, consistent spacing between adjacent buttons, and adequate edge padding so nothing is clipped against the viewport.

---

## Hard rules — security and dependencies (apply now and always)

### For the demo

- **Install nothing into the demo.** Do not run any package installer for the demo, and `demo/` must contain no `package.json`, `node_modules`, or lockfile. (One exception exists for isolated dev **test tooling** — see "Test tooling" below — which never lives in `demo/`; the demo artifact itself stays dependency-free.)
- **No backend.** No server runtime, API, or database.
- **No remote code at runtime.** Do not add `<script src="…cdn…">` or remote stylesheet links that load third-party code on page load. Write the CSS by hand. If a remote asset ever seems genuinely necessary, **stop and ask first**; if approved, pin it and use Subresource Integrity (`integrity="sha384-…"`).
- **Preview** with a runtime already on the machine — e.g. `python3 -m http.server` run from `HR_System/demo/`. Opening `index.html` directly is also fine.
- **Do not install or recommend an editor extension** (e.g. a "Live Server") to run the demo. Editor marketplaces are an active supply-chain target; `python3 -m http.server` needs none.

If a task seems to require a dependency or a backend, it has left the demo's scope. Stop and ask the human.

### Operating-system and editor packages (always)

- **Do not install system packages** via AUR, `yay`, `pacman`, or any OS package manager without explicit human approval. When approved, prefer the distribution's official vetted repositories over user-contributed ones (AUR is unvetted and has been used to deliver malware).
- **Do not install editor extensions** or pull them from any marketplace.
- **No pipe-to-shell installers** (`curl … | sh`, `wget … | bash`). Ever.

---

## Images, video, and other media (all phases)

Do **not** generate, download, or fetch images, video, audio, fonts, logos, or any other binary media yourself, and do not pull them from a CDN or stock-media site.

When the project needs a media asset, produce a short **asset request** and let the human deliver the file:

- **Filename and path** where it should go (e.g. `HR_System/demo/assets/corvinum-logo.svg`).
- **Generation prompt** — a precise prompt the human can paste into an image/video generator (subject, style, composition, palette, mood, transparent vs solid background, any text to include or avoid).
- **Specs** — format, dimensions/aspect ratio, approximate file size, and for video its length and whether audio is needed.
- **Runbook** — where the asset is used in the code and what happens once the human drops the file in (e.g. "referenced as the `--logo-corvinum` background; no code change needed once `corvinum-logo.svg` exists").

Until the real asset arrives, use a clearly labelled placeholder (a neutral box, inline SVG shape, or solid-colour block with the asset name as alt text) so the layout works. Never leave a broken image link, and never invent a remote URL for an asset that does not exist.

---

## Phase 2 — production build (future; these rules apply the moment any dependency is introduced)

### Package manager

- **pnpm only.** Never `npm`, `npx`, or `yarn` — not for installs, not for one-off execution.
- **Require pnpm v11 or newer**, pinned via Corepack. v11 ships the secure defaults below.
- **No global installs** (`pnpm add -g`) and **no `pnpm dlx`** of arbitrary packages.

### Required `pnpm-workspace.yaml` hardening

Keep these explicit even where they are pnpm 11 defaults, so the posture is enforced and auditable:

```yaml
# pnpm-workspace.yaml
minimumReleaseAge: 1440          # 1-day cooldown; raise to 10080 for one week
minimumReleaseAgeStrict: true    # fail the install if only a too-new version matches
blockExoticSubdeps: true         # transitive deps may not resolve via git / tarball / http
minimumReleaseAgeExclude: []     # ONLY vetted emergency security patches, added per-incident with human sign-off
```

Rationale: most malicious package versions are detected and pulled within hours, so a 1-day cooldown filters out smash-and-grab attacks. Do not lower `minimumReleaseAge` below 1440 or disable `blockExoticSubdeps` without explicit human approval.

### Install scripts (lifecycle hooks)

- Dependency `preinstall` / `install` / `postinstall` scripts are the primary attack delivery mechanism and stay **disabled by default**.
- A dependency may run build scripts only after a human reviews why, by adding it to the `allowBuilds` allowlist.

### Adding a dependency

- **No new dependency without explicit human approval.** Prefer the platform, standard library, or a few lines of your own code over a package.
- When proposing one, state: exact package and version, what it does, why writing it ourselves is worse, its maintenance/popularity signals, and whether it needs build scripts.
- **Pin exact versions** (no `^` / `~`); rely on the committed lockfile.
- **Registry sources only** — no git/tarball/`http` direct dependencies.
- Commit `pnpm-lock.yaml`; install with `pnpm install --frozen-lockfile` by default and in CI.
- Run `pnpm audit` after dependency changes and report findings.

### CI / actions (when added)

- Pin GitHub Actions to a commit SHA, not a mutable tag.
- Pin container images to a digest (`@sha256:…`), not `latest`.

---

## Test tooling — runs in a pinned Docker container (isolated)

Headless-browser testing uses **Playwright**, and it runs **inside a pinned Docker container, not on the host.** This contains the riskiest moment — dependency install and any postinstall hook — away from host SSH keys, tokens, browser profiles, and env vars, and it removes the browser-download vector entirely because browsers are pre-baked into the official image.

**Prerequisite:** Docker must be available in the guest (Ubuntu 24.04). Verify it (`docker --version`) and record the result in `ENVIRONMENT.md`. If Docker is not available, **stop and ask** — do not fall back to a host install of Playwright/Puppeteer without explicit approval.

- **Image:** the official Playwright image, **pinned by digest** — `mcr.microsoft.com/playwright:vX.Y.Z-noble@sha256:…` (the `noble` tag matches the Ubuntu 24.04 guest). Browsers are pre-baked; no browser download happens on the host or in the container.
- **Dev-tooling workspace** (Playwright config, test specs, `package.json` with `@playwright/test` pinned exact, `pnpm-lock.yaml`) lives at the `HR_System/` root — **outside `demo/`**. It is dev tooling only, **not** the production `src/ modules/ clients/` scaffold, which is still not to be built.
- **Dependency install happens inside the container build** (`pnpm install --frozen-lockfile`, browser download skipped since the image already has them). The install is contained in an image layer and never runs on the host.
- **The test run is airtight:**
  - mount `demo/` **read-only**; write screenshots/results to a **separate writable artifacts directory** only;
  - run with **`--network none`** — the demo is served on localhost inside the container, so no external network is needed at run time;
  - run as the image's **non-root** user;
  - pass **no host secrets** — no SSH keys, tokens, or env vars; none are required;
  - the container is disposable and cannot reach host source or credentials.
- **The demo stays dependency-free and static.** The container and tooling are never a runtime dependency of `demo/`; what you present and ship is unchanged.
- Keep Playwright in `devDependencies` only. Record the Playwright version and the **pinned image digest** in `ENVIRONMENT.md`, and the run command in `test_journal.md`.

This **supersedes** the earlier browser-download postinstall exception — with the container image, no `allowBuilds` browser-download carve-out is needed. Everything else stands: pnpm only, no global installs, no pipe-to-shell installers, no OS or editor-marketplace installs, no other dependencies without approval.

---

## Project journals — living docs you must keep current

Maintain four markdown journals at the **`HR_System/` root**. These are the one allowed exception to the "work only in `demo/`" rule. Create them if they don't exist, and update the relevant one as part of every change — not as an afterthought. They are how context survives between sessions and between different agents.

- **`BUILD_JOURNAL.md`** — a running, dated log of what was built and why. Each entry: date, what changed, decisions made and their rationale, anything deferred, and the next step. Append new entries; don't rewrite history.
- **`ENVIRONMENT.md`** — the development environment: OS, available runtimes and tools (e.g. `python3` for the static server, the browser used), versions, and explicitly what is *not* available. Record what you discover and keep it accurate. If a tool you need is missing, note it here and ask — do not install it.
- **`deployment_journal.md`** — how the current build is deployed/served right now. For the demo this is the static-serve method (e.g. `python3 -m http.server` from `demo/`, or opening `index.html`). Update it whenever the deploy method changes.
- **`test_journal.md`** — how the build is tested locally: the steps you run, the manual checklist (from the build spec's test plan), what passed or failed, and any known issues. Update it each time you test.

Treat "journals updated" as part of done — when a unit of work is finished, the relevant journals should already reflect it.

---

## How to work here

- Keep all current work inside `HR_System/demo/`. Do not touch or create anything elsewhere in `HR_System/` yet — the only exception is the project journals above, which live at the `HR_System/` root.
- Match the design direction described in the build spec; write interface copy in plain, active-voice, sentence case ("Approve hire", "Send pickup notice").
- Make small, reviewable changes and explain what each screen/file does.

### Ask questions; don't guess

- When anything about the design or behaviour is unclear or underspecified — layout, visual direction, copy, a screen's contents, an interaction, edge cases, scope — **ask the human before building it.** Ask as many questions as you need; batch them so they can be answered in one pass. A clarifying question is always preferred over a confident guess that has to be redone.
- Surface ambiguities early, while they are cheap to resolve, not after a screen has been built around an assumption.

### Design references in the repo (follow these)

- **Design guidance:** the official `frontend-design` skill is in the repo at `demo/frontend-design/SKILL.md`. Follow it for aesthetic direction — define a token system first, spend boldness on one signature element, and self-critique against generic SaaS-dashboard defaults before coding.
- **Typography is decided** in `typography_and_fonts.md` (in `demo/`). Use **Option A** by default: system-font stacks via the given CSS variables, with **no remote stylesheets and no downloaded font files**. Only switch to Option B (self-hosted faces) if the human has delivered font files into `demo/assets/fonts/`. Do not load fonts from Google Fonts or any CDN.

### Request more skills when you need them

- Design and build guidance can be supplied as **skill files** (a `SKILL.md` — portable markdown instructions).
- If you reach a part you're unsure how to design or build well and a skill would help, **ask the human to provide the relevant skill** — name what you need (e.g. "a skill for accessible data tables"). The human fetches and delivers it, the same way they deliver media assets.
- Do **not** install skills via a plugin or marketplace command yourself — that is prohibited by the security rules above. Only use skill markdown the human has placed in the repo.

## When in doubt

Stop and ask before installing, adding, or fetching anything that executes code. A blocked task is recoverable; a compromised dev or CI environment is not.
