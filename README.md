# StabMBQC Game – Stabilizer Survival

This repository contains a small web-based game built around your StabMBQC ideas.
The project is intentionally split into two main parts:

- `docs/`: a static front-end (HTML/CSS/JS) suitable for GitHub Pages.
- `backend/`: a Python package that does all the quantum/heavy lifting (Stim, Qiskit, etc.).

## Layout

```text
.
├── docs/           # static site: index.html, JS, CSS, level JSON, assets
└── backend/        # Python: Stim/Qiskit logic, level/round generation
```

## Typical workflows

### 1. Running the front-end locally

From the repo root:

```bash
python -m http.server 8000
```

Then open:

- <http://localhost:8000/docs/>

The front-end will load `docs/levels/level-1.json` and display the game.

### 2. Generating levels with Python (backend)

Use the CLI script in `backend/` to generate JSON + assets:

```bash
python -m backend.cli_generate \
  --level 1 \
  --num-rounds 5 \
  --out-json docs/levels/level-1.json \
  --assets-dir docs/assets
```

This will:

- Call into `backend.qc-main0` to generate stabilizers/candidates per round.
- Optionally render circuit/graph images (once you implement `rendering.py`).
- Produce a `level-1.json` file that the front-end can immediately use.

### 3. Where to put the quantum logic

All the physics-specific code (Stim, stabilizer reasoning, extractability checks) should
live in `backend/qc-main0.py`. The rest of the backend modules are thin wrappers that
turn your physics into front-end–friendly JSON.
