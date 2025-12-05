# Ideas & Progress Log

A running, time‑stamped record of major steps, design choices, and structural changes in the StabMBQC Game project.

---

## 2025‑12‑05 — Initial Game Engine Architecture

* Designed core browser game loop: **slides → level → rounds → next level**.
* Implemented: intro slides, skip button, rules overlay, restart‑game + restart‑level logic.
* Added timed rounds, per‑round success/fail feedback, safe/unsafe detection.
* Separated back‑end logic into JSON‑driven round specifications.

## 2025‑12‑05 — Backend Architecture Plan (Python)

* Defined clean separation: `docs/` (frontend) vs `backend/` (quantum engine).
* Decided backend generates **JSON + assets** for levels.
* Created proposed modules: `qc-main0.py`, `model.py`, `rounds.py`, `rendering.py`, `cli_generate.py`.
* Clarified workflow for Level‑1 and Level‑2 physics (CZs, Pauli rotations, Stim tableau updates, etc.).

## 2025‑12‑05 — Repo Bootstrap Script

* Wrote full bash script that:

  * Auto‑creates backend package structure.
  * Injects Python stubs + READMEs.
  * Defines example CLI tool and placeholder rendering functions.
* Updated READMEs for project root, docs/, backend/.
* Prepared repo for Stim/Qiskit integration.

---

*(Use the command **UPDATE LOG** anytime to append new entries automatically.)*
