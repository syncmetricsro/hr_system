# CLAUDE.md — HR_System

Project instructions for Claude Code. These rules are binding. When a rule here conflicts with a request, follow the rule and tell the human why.

---

## Project state

- The only thing being built right now is the **demo prototype** in `HR_System/demo/`.
- The demo is **static vanilla HTML, CSS, and JavaScript**. It has **no backend and no dependencies**, by design.
- The future production application will live in the same `HR_System/` folder later. Its package rules are in the second half of this file. Do **not** scaffold or build it yet.

---

## Phase 1 — Demo (current)

### Hard rules

- **Install nothing into the demo.** No installer is run for the demo, and `demo/` contains no `package.json`, `node_modules`, or lockfile. (One exception exists for isolated dev **test tooling** — see "Test tooling" below — which never lives in `demo/`; the demo artifact itself stays dependency-free.)
- **No backend.** No server runtime, no API, no database. State lives in plain in-memory JS and resets on reload — that is intended.
- **No framework, bundler, transpiler, or build step.** Plain HTML/CSS/JS only.
- **No remote code at runtime.** Do not add `<script src="…cdn…">` or remote stylesheet links that pull third-party code when the page loads. Write the CSS by hand. If a remote asset ever seems genuinely necessary, stop and ask first; if approved, it must be version-pinned with Subresource Integrity (`integrity="sha384-…"`).
- **Previewing the demo:** serve it with the language runtime already on the machine — e.g. `python3 -m http.server` run from `HR_System/demo/`. Opening `index.html` directly in a browser is also fine.
- **Do not install or recommend any editor extension** (e.g. a "Live Server" VS Code extension) to run the demo. Editor marketplaces are an active supply-chain attack target; `python3 -m http.server` needs no extension.

If a task seems to require a dependency or a backend, it has left the scope of the demo. Stop and ask the human before doing anything.

---

## Images, video, and other media (all phases)

Do **not** generate, download, or fetch images, video, audio, fonts, logos, or any other binary media yourself, and do not pull them from a CDN or stock-media site.

When the project needs a media asset, instead produce a short **asset request** and let the human deliver the file:

- **Filename and path** where the asset should be placed (e.g. `HR_System/demo/assets/corvinum-logo.svg`).
- **Generation prompt** — a precise prompt the human can paste into an image/video generator (subject, style, composition, palette, mood, background — transparent vs solid, any text to include or avoid).
- **Specs** — format, dimensions/aspect ratio, approximate file size, and for video its length and whether audio is needed.
- **Runbook** — exactly where it gets used in the code and what to do once the human drops the file in (e.g. "reference it as `--logo-corvinum` background; no code change needed once `corvinum-logo.svg` exists").

In the meantime, use a clearly labelled placeholder (a neutral box, an inline SVG shape, or a solid-colour block with the asset name as alt text) so the layout works without the real asset. Never leave a broken image link, and never invent a remote URL for an asset that does not exist.

---

## Phase 2 — Production build (future; rules apply the moment any dependency is introduced)

### Package manager

- **pnpm only.** Never run `npm`, `npx`, or `yarn` — not for installs, not for one-off script execution. If you see yourself reaching for `npx`, stop.
- **Require pnpm v11 or newer**, pinned via Corepack (`corepack use pnpm@latest`). v11 ships the secure defaults below; older versions do not.
- **No global installs** (`pnpm add -g`) and **no `pnpm dlx`** of arbitrary packages. Tools the project needs are project dev-dependencies, vetted like any other.

### Required hardening in `pnpm-workspace.yaml`

Keep these set explicitly even though some are pnpm 11 defaults — the file makes the posture enforced and auditable:

```yaml
# pnpm-workspace.yaml
minimumReleaseAge: 1440          # 1-day cooldown; raise to 10080 for one week
minimumReleaseAgeStrict: true    # fail the install if only a too-new version matches, rather than silently doing something unexpected
blockExoticSubdeps: true         # transitive deps may not resolve via git / tarball / http sources
minimumReleaseAgeExclude: []     # ONLY for vetted emergency security patches, added per-incident with human sign-off
```

The cooldown exists because most malicious package versions are detected and pulled within hours; a 1-day delay filters out the smash-and-grab attacks. Do not lower `minimumReleaseAge` below 1440 or disable `blockExoticSubdeps` without explicit human approval.

### Install scripts (lifecycle hooks)

- Dependency build/lifecycle scripts (`preinstall`, `install`, `postinstall`) are the primary delivery mechanism for these attacks and must stay **disabled by default**.
- A dependency may run build scripts only if it is added to the `allowBuilds` allowlist **after a human has reviewed why it needs to**.

### Adding a dependency

- **No new dependency is added without explicit human approval.** Prefer the platform, the standard library, or a few lines of your own code over pulling a package. Most small utilities are not worth a dependency.
- When proposing one, present: the exact package and version, what it does, why writing it ourselves is worse, its maintenance/popularity signals, and whether it requires build scripts.
- **Pin exact versions** (no `^` / `~`) in `package.json`; rely on the committed lockfile.
- **Registry sources only.** No git URLs, tarball URLs, `http(s)` direct dependencies, or local exotic protocols in top-level dependencies.
- Always install reproducibly: commit `pnpm-lock.yaml` and use `pnpm install --frozen-lockfile` by default and in CI.
- Run `pnpm audit` after dependency changes and report findings.

### Operating-system and editor packages

- **Do not install system packages** via AUR, `yay`, `pacman`, or any OS package manager without explicit human approval; when approved, prefer the distribution's official vetted repositories over user-contributed ones (AUR is unvetted and has been used to deliver malware).
- **Do not install editor extensions**, and do not pull them from any marketplace.
- **No pipe-to-shell installers** (`curl … | sh`, `wget … | bash`). Ever.

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
- **`test_journal.md`** — how the build is tested locally: the steps you run, the manual checklist, what passed or failed, and any known issues. Update it each time you test.

Treat "journals updated" as part of done — when a unit of work is finished, the relevant journals should already reflect it.

---

## How to work here

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

---

## When in doubt

Stop and ask the human before installing, adding, or fetching anything that executes code. A blocked task is recoverable; a compromised dev or CI environment is not.
