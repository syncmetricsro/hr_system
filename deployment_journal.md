# Deployment Journal

## 2026-06-13

Current deployment method:
- Static files only.
- Primary previews:
  - Internal combined build: open `demo/internal/index.html`.
  - CorvinumEU client build: open `demo/corvinum/index.html`.
  - Jober client build: open `demo/jober/index.html`.
- Optional local server: run `python3 -m http.server` from `demo/`, then open:
  - `http://127.0.0.1:8000/internal/`
  - `http://127.0.0.1:8000/corvinum/`
  - `http://127.0.0.1:8000/jober/`

Verified today:
- The demo is split into the three static build folders above.
- Browser verification is recorded in `test_journal.md`.

No deployment artifacts, backend service, package files, or build output are required.
