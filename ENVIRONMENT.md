# Environment

Last updated: 2026-06-13

System:
- OS: Ubuntu 24.04.4 LTS in VirtualBox, Linux kernel `6.17.0-35-generic`.
- Workspace: `/home/disane/Development/HR_System`.
- Git: this folder is not currently inside a Git repository.

Available local tools used:
- `python3`: Python 3.12.3.
- `node`: v22.22.3, used only for JavaScript syntax and Chromium DevTools Protocol checks.
- `chromium`: Chromium 148.0.7778.215, used for headless browser verification and screenshots.
- `docker`: Docker version 29.5.3, build d1c06ef.
- `rg`: available for text scans.

Browser test tooling:
- Playwright is permitted only through the isolated Docker workflow described in `AGENTS.md` and `CLAUDE.md`.
- Verified Playwright image tag: `mcr.microsoft.com/playwright:v1.60.0-noble`.
- Verified repo digest from `docker inspect`: `mcr.microsoft.com/playwright@sha256:9bd26ad900bb5e0f4dee75839e957a89ae89c2b7ab1e76050e559790e946b948`.
- Pinned image used for tests: `mcr.microsoft.com/playwright:v1.60.0-noble@sha256:9bd26ad900bb5e0f4dee75839e957a89ae89c2b7ab1e76050e559790e946b948`.
- `@playwright/test` is pinned to exact version `1.60.0`, matching the image version.
- Host `pnpm` is 10.33.2, below the v11 policy target. Playwright dependency setup is performed inside the pinned container workflow, not as a host install.

Not used:
- No package manager, dependency installer, framework, bundler, remote runtime code, remote stylesheet, font download, image generation, or media download is used by the demo runtime.

Notes:
- Headless Chromium prints a local VAAPI/GPU warning in this VM. The app itself produced no runtime or console errors in the browser checks.
