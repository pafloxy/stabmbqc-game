## StabMBQC Game – Local Testing Plan

This plan is for a coding agent with full local access to `/home/pafloxy/Documents/INRIAProjectVault/connected-projects/stabmbqc-game`. The goal is to add scripted regression checks for `docs/main.js` + `docs/levels/level-1.json` rendering, by spinning up a local server and auto-clicking through all flows.

### Goals
- Serve the `docs/` folder locally (GitHub Pages equivalent).
- Headless browser tests that load the app, walk through intro slides, info overlay, all round steps/options, and verify rendering (no console errors, missing fetches, or MathJax crashes).
- Sanity checks that every referenced asset/markdown file exists and returns 200.

### Prereqs the agent should install/verify
- Node 18+ and npm/pnpm/yarn.
- Install Playwright (`npm i -D playwright`) and optionally `http-server` or `serve` for static hosting. If adding deps is undesirable, use `python3 -m http.server` instead.
- Ensure `docs/.nojekyll` exists if testing Pages parity for raw `.md` fetches.

### Files/directories to add under `docs/testing0`
1) `package.json` (dev deps: playwright, optionally start-server-and-test or http-server).
2) `playwright.config.ts` (baseURL pointing to `http://localhost:4173` or chosen port; retries=0/1; headless true; screenshot on failure).
3) `scripts/serve.js` or `scripts/serve.sh` to run a static file server rooted at `docs/` (e.g., `http-server . -p 4173` or `python3 -m http.server 4173`).
4) `tests/content.spec.ts`:
   - Fetch every `textPath`, `contextPath`, `promptPath`, and asset path declared in `levels/level-1.json`; assert 200 and non-empty body.
5) `tests/flows.spec.ts`:
   - Load `/index.html`; wait for app ready.
   - Step through intro slides: next/prev, ensure slide body populated (non-empty), no console errors.
   - Open info overlay (rules/hints), toggle tabs, close.
   - For each round: verify context renders; for each step: click each option, assert feedback renders; if a wrong answer causes game over, restart and continue to cover all options; ensure victory path works.
   - Verify MathJax typeset completion (e.g., wait for `mjx-container` presence after slides/feedback render).
6) `tests/console.spec.ts`:
   - Attach to console; fail on errors or failed network requests (404/500) except known favicon.

### Implementation steps for the agent
1) From `docs/`, create `testing0/` and initialize npm (`npm init -y`).
2) Install dev deps: `npm i -D playwright http-server` (or omit http-server if using Python).
3) Add `playwright.config.ts` with baseURL and testDir `testing0/tests`.
4) Add scripts to `package.json`:
   - `"serve": "http-server . -p 4173"`,
   - `"test:ui": "start-server-and-test serve http://localhost:4173 \"playwright test\""` or use a custom small runner to spawn server + tests.
5) Implement `tests/content.spec.ts`:
   - Read `../levels/level-1.json`, collect all `textPath`, `contextPath`, `promptPath`, `assets.*`, ensure request to each returns 200 via Playwright `page.goto(baseURL + '/' + path)` with `waitUntil: 'networkidle'`.
6) Implement `tests/flows.spec.ts`:
   - Launch page, wait for main screen.
   - Intro carousel: click next until end, ensure slide text area not “Loading…” and length > 0.
   - Info overlay: open, switch tabs, ensure content present, close.
   - Round coverage:
     - For each step, iterate options: click option, assert feedback appears. If wrong answer triggers game over, click “Restart” (or equivalent) and continue; record which option yielded victory and proceed to next step/round.
     - After final correct path, assert victory screen appears.
   - Throughout, listen for `console` events; fail on `error`/`warning` that match missing resource patterns.
7) Implement `tests/console.spec.ts`:
   - Visit home; capture failed requests via `page.on('requestfailed', …)`; fail on 4xx/5xx except favicon; capture `page.on('console', …)` and fail on `type === 'error'`.
8) Add a short `README.md` inside `testing0/` describing how to run: `npm install`, `npm run serve` in one terminal, `npm run test:ui` in another (or single command if using start-server-and-test).

### Validation the agent should do
- Run `npm run test:ui` locally; ensure zero failures.
- Manually hit `http://localhost:4173/content/slides/intro-01.md` to confirm raw markdown served (parity with GitHub Pages when `.nojekyll` present).
- Capture artifact (screenshots on failure) to diagnose.

### Notes on app specifics (from current code)
- `main.js` uses `BASE_PATH` auto-detected; local server should serve at root to avoid path issues.
- Slide loading is via fetch of `.md`; MathJax renders after typewriter effect. Tests should wait for `mjx-container` or text length > 0 before proceeding.
- If `.nojekyll` is missing on Pages, `.md` fetch will 404; the content test will catch this locally when served raw. To emulate Pages with Jekyll, agent could also run a variant that serves `.md` as 404 to ensure code handles errors (optional).
