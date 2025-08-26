# StabMBQC Game: Implementation Plan for Rounds/Levels (Codex-ready)

This is a hand-off document for implementing the next iteration of the game: **progressively harder rounds**, each round optionally containing multiple **steps** (choose measurement / choose extracted PES / choose Clifford / update based on outcome), with **intro slides**, **info page**, **restart**, **skip via cheat-code**, and a **terminal/Atari aesthetic**.

Repo split (already in place):

* `docs/` = static site (GitHub Pages)
* `backend/` = Python generators (Stim/Qiskit + rendering)

---

## 0. High-level goal

We want the frontend to be completely static and deterministic:

* It loads a JSON file from `docs/levels/*.json`.
* It renders slides + rounds.
* It checks answers against `correct_option_id` (and optionally displays explanations).

Separately, the Python backend should be able to:

* Generate/validate round instances.
* Optionally render **circuit PNGs** and **graph PNGs** into `docs/assets/`.
* Write JSON into `docs/levels/`.

For Secret Santa (deadline soon):

* It’s fine to **hand-author JSON**.
* Backend can be used only to **verify correctness** and **export images**.

Later:

* Backend can generate full rounds procedurally.

---

## 1. Game UX: screens and navigation

### Required screens

1. **Home / Title screen**

* Buttons: `Start`, `Info`, `Restart` (Restart can just reload the app state to Home)

2. **Intro slides** (non-interactive except navigation)

* Buttons: `Next`, `Back`, `Skip Intro`
* Slides can show text + images.

3. **Rounds flow**

* Each round is a sequence of **steps**.
* Per step:

  * show prompt text
  * show optional images (circuit/graph)
  * show multiple-choice options
  * enforce a timer (if desired)
* Buttons: `Submit`, `Next Step`, `Next Round`, `Restart Game`, `Info`

4. **Info page**

* A “rulebook” view.
* Should be accessible anytime during rounds.

5. **Game Over**

* Triggered by wrong answer or timer.
* Buttons: `Restart Game`, `Back to Home`

6. **Victory / End**

* After final round.
* Buttons: `Restart Game`, `Back to Home`

### Cheat-code skip

* A `Skip Round` button appears during round flow.
* On click: prompt for cheat code.
* If matches `config.cheat.code` (in JSON): advance to next round (or next step).

---

## 2. JSON format: new schema

We’ll implement a single JSON file per “campaign” (or level pack). Example location:

* `docs/levels/level-1.json`

The front-end must be written so it supports:

* intro slides
* N rounds
* each round has steps

### Proposed JSON schema (v1)

```json
{
  "schema_version": "1.0",
  "meta": {
    "title": "Stabilizer Survival",
    "subtitle": "Harold Edition",
    "theme": "terminal",
    "assets_base": "assets"
  },
  "config": {
    "timer": {"enabled": true, "seconds_per_step": 30},
    "cheat": {"enabled": true, "code": "HAROLD"}
  },
  "info": {
    "markdown": "# Rulebook\n...",
    "images": ["info/stabilizer_rules.png"]
  },
  "intro_slides": [
    {
      "id": "intro-1",
      "title": "Your kingdom state is under attack",
      "body_markdown": "Bob is entangling and measuring...",
      "images": ["slides/intro-1.png"]
    }
  ],
  "rounds": [
    {
      "id": "r1",
      "title": "Warm-up: harmless measurement",
      "difficulty": 1,
      "context_markdown": "Alice holds $\\ket{\\mathcal{S},\\psi}$ ...",
      "assets": {
        "circuit_image": "rounds/r1-circuit.png",
        "graph_image": "rounds/r1-graph.png"
      },
      "steps": [
        {
          "id": "r1-s1",
          "kind": "select_measurement",
          "prompt_markdown": "Charlie offers these Pauli measurements. Pick one that is non-destructive.",
          "options": [
            {"id": "A", "label": "$Z_{3}X_{4}$", "detail_markdown": "..."},
            {"id": "B", "label": "$X_{1}Z_{3}$", "detail_markdown": "..."}
          ],
          "answer": {"correct_option_id": "A"},
          "feedback": {
            "on_correct_markdown": "Nice. This only kills one stabilizer generator.",
            "on_wrong_markdown": "Oops. That was a logical measurement—game over."
          },
          "timer": {"enabled": true, "seconds": 25}
        },
        {
          "id": "r1-s2",
          "kind": "select_clifford",
          "prompt_markdown": "Given Bob’s CZ attack, which Clifford $U_{\\mathrm{Cl}}$ maps $\\langle S'\\rangle$ to $\\langle \\tilde S\\rangle$?",
          "options": [
            {"id": "A", "label": "$U_{\\mathrm{Cl}}=\\mathrm{CZ}(0,3)\\mathrm{CZ}(1,4)$"},
            {"id": "B", "label": "$U_{\\mathrm{Cl}}=H_{0}\\mathrm{CZ}(0,2)$"}
          ],
          "answer": {"correct_option_id": "A"},
          "feedback": {"on_correct_markdown": "Yup.", "on_wrong_markdown": "Nope."}
        }
      ]
    }
  ]
}
```

### Notes

* `prompt_markdown` and `label` are treated as markdown-like strings; **math rendering is optional** (see section 8 for minimal KaTeX integration if desired).
* `assets_base` allows easy relocation.
* Each `step.timer` overrides default `config.timer`.

---

## 3. Front-end implementation plan (docs/)

Target files:

* `docs/index.html`
* `docs/main.js`
* `docs/style.css`

### 3.1 State machine

Implement a single global `appState`:

```js
const appState = {
  phase: "home", // home | intro | info | round | gameover | victory
  introIndex: 0,
  roundIndex: 0,
  stepIndex: 0,
  selectedOptionId: null,
  timer: { active: false, remaining: 0, handle: null },
  stats: { correct: 0, wrong: 0 }
};
```

Core transitions:

* `home -> intro` on Start
* `intro -> round` when intro ends or Skip Intro
* `round -> info` temporarily (store previous phase to return)
* `round -> gameover` on wrong/timer
* `round -> victory` after last round/step

### 3.2 Rendering strategy

Use “render by phase”:

* `renderHome()`
* `renderIntro()`
* `renderInfo()`
* `renderRound()`
* `renderGameOver()`
* `renderVictory()`

Each render function:

* writes into a single root container (e.g. `<div id="app"></div>`)
* wires event handlers after DOM injection

### 3.3 Timer logic

Timer rules:

* Start timer at step render.
* If player submits before timer ends: stop timer.
* If timer hits 0: trigger `gameover`.

Implementation sketch:

```js
function startTimer(seconds, onExpire) {
  stopTimer();
  appState.timer.active = true;
  appState.timer.remaining = seconds;

  appState.timer.handle = setInterval(() => {
    appState.timer.remaining -= 1;
    updateTimerUI(appState.timer.remaining);
    if (appState.timer.remaining <= 0) {
      stopTimer();
      onExpire();
    }
  }, 1000);
}

function stopTimer() {
  if (appState.timer.handle) clearInterval(appState.timer.handle);
  appState.timer.handle = null;
  appState.timer.active = false;
}
```

### 3.4 Cheat-code skip

* Button `Skip Round` only in `renderRound()`.
* Prompt `window.prompt("Enter cheat code")`.
* If matches JSON `config.cheat.code`: `advanceToNextRound()`.

### 3.5 Restart game

A hard reset function:

```js
function restartGame() {
  stopTimer();
  appState.phase = "home";
  appState.introIndex = 0;
  appState.roundIndex = 0;
  appState.stepIndex = 0;
  appState.selectedOptionId = null;
  appState.stats = { correct: 0, wrong: 0 };
  render();
}
```

---

## 4. Backend implementation plan (backend/)

Backend is for:

* validating round correctness
* generating assets (circuit/graph PNG)
* (later) generating rounds procedurally

Current structure (already present):

* `backend/cli_generate.py`
* `backend/model.py`
* `backend/rounds.py`
* `backend/qc-main0.py`
* `backend/rendering.py`

### 4.1 Data model (backend/model.py)

Define dataclasses mirroring the JSON schema.

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class Option:
    id: str
    label: str
    detail_markdown: str = ""

@dataclass
class StepAnswer:
    correct_option_id: str

@dataclass
class Step:
    id: str
    kind: str
    prompt_markdown: str
    options: List[Option]
    answer: StepAnswer
    feedback: Dict[str, str] = field(default_factory=dict)
    timer: Optional[Dict[str, Any]] = None

@dataclass
class RoundAssets:
    circuit_image: Optional[str] = None
    graph_image: Optional[str] = None

@dataclass
class Round:
    id: str
    title: str
    difficulty: int
    context_markdown: str
    assets: RoundAssets
    steps: List[Step]

@dataclass
class Campaign:
    schema_version: str
    meta: Dict[str, Any]
    config: Dict[str, Any]
    info: Dict[str, Any]
    intro_slides: List[Dict[str, Any]]
    rounds: List[Round]
```

Also implement `to_json()` and `from_json()`.

### 4.2 QC core (backend/qc-main0.py)

This file should provide:

* parsing and formatting Pauli strings
* computing commutation and anti-commutation
* applying CZ conjugation rules to stabilizers
* checking “logical vs non-logical measurement” (for the simplified Level-1 notion)

Even if you manually author rounds, **this file is used to verify**.

#### Minimal Stim helpers

```python
import stim

def pauli(s: str) -> stim.PauliString:
    # Example: "Z3*X4" or "Z3 X4"; normalize upstream.
    return stim.PauliString(s.replace("*", " "))

def commutes(p: stim.PauliString, q: stim.PauliString) -> bool:
    return p.commutes(q)

def anticommutes(p: stim.PauliString, q: stim.PauliString) -> bool:
    return not p.commutes(q)
```

#### Conjugation by CZ on Paulis

You can implement CZ conjugation via Stim circuit conjugation, or explicit rule:

* $\mathrm{CZ}(a,b): X_{a} \mapsto X_{a}Z_{b}$
* $\mathrm{CZ}(a,b): X_{b} \mapsto Z_{a}X_{b}$
* $Z$ unchanged

Stim approach:

```python
def conjugate_by_cz(p: stim.PauliString, a: int, b: int) -> stim.PauliString:
    c = stim.Circuit()
    c.append("CZ", [a, b])
    return p.after(c)
```

(If `after` is not available in your Stim version, use: build a tableau or do manual rules.)

#### Updating a stabilizer generating set under Bob’s CZ attack

```python
def update_generators_under_cz(gens: list[stim.PauliString], cz_edges: list[tuple[int,int]]):
    out = []
    for g in gens:
        gg = g
        for (a,b) in cz_edges:
            gg = conjugate_by_cz(gg, a, b)
        out.append(gg)
    return out
```

#### Simplified “non-destructive measurement” predicate (for early rounds)

Your scribble rule: measurement $M$ is safe if it anticommutes with exactly one generator of $\langle \tilde S\rangle$ (kills only that generator), rather than acting logically.

```python
def is_safe_measurement(M: stim.PauliString, stab_gens: list[stim.PauliString]) -> bool:
    anti = sum(1 for g in stab_gens if anticommutes(M, g))
    return anti == 1
```

Later, replace this heuristic by your full “not logical wrt $\langle\tilde S\rangle$” definition.

### 4.3 Rendering (backend/rendering.py)

Goal: generate PNGs stored under `docs/assets/...`.

Two paths:

1. Qiskit: Stim -> Qiskit circuit -> draw to matplotlib -> PNG.
2. Pure matplotlib: draw a small schematic (CZ edges + rotations + measurement marks).

For speed, implement a minimal “schematic circuit drawer”:

* wires are horizontal lines
* CZ as vertical line with dots
* rotations as boxes (`X(θ)`, `Z(θ)`, etc.)
* measurement as `M` box

Provide:

```python
def render_circuit_png(round_id: str, out_path: str, spec: dict):
    """spec may include: n_qubits, cz_edges, rotations, measured_qubits, labels"""
    ...
```

Also:

```python
def render_graph_png(round_id: str, out_path: str, graph_spec: dict):
    """Optional: show interaction graph / open graph."""
    ...
```

### 4.4 Round definitions (backend/rounds.py)

For now, implement **only validation**:

* load JSON
* for each round/step check that:

  * option IDs are unique
  * correct option exists
  * referenced assets exist under `docs/assets/`
  * optional: run QC checks and warn if inconsistent

```python
import json
from pathlib import Path

from .qc_main0 import pauli, is_safe_measurement

def validate_campaign_json(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text())

    # basic checks
    if "rounds" not in data:
        errors.append("Missing rounds")
        return errors

    for r in data["rounds"]:
        for step in r.get("steps", []):
            opts = step.get("options", [])
            opt_ids = [o["id"] for o in opts]
            if len(set(opt_ids)) != len(opt_ids):
                errors.append(f"Duplicate option ids in {r['id']}:{step['id']}")

            ans = step.get("answer", {}).get("correct_option_id")
            if ans not in opt_ids:
                errors.append(f"Answer id not found in options {r['id']}:{step['id']}")

    return errors
```

### 4.5 CLI (backend/cli_generate.py)

Keep CLI simple:

* `--in-json docs/levels/level-1.json`
* `--assets-dir docs/assets`
* `--render` to regenerate PNG assets
* `--validate` to run checks

Pseudo-interface:

```bash
python -m backend.cli_generate --validate --in-json docs/levels/level-1.json
python -m backend.cli_generate --render --in-json docs/levels/level-1.json --assets-dir docs/assets
```

---

## 5. Mapping your scribble example into 3–4 rounds

We’ll build rounds all based on the *same core circuit idea*:

* Alice registers + Bob ancillas in $\ket{+}$
* Bob attacks via CZ edges (and later rotations)
* Charlie measures some Pauli string(s)
* Player chooses which measurement / extracted unitary / clifford is consistent.

### Round plan

**Round 1 (easy):**

* Show $\langle S'\rangle$ and $U_{\mathrm{Cl}}$ effect is either given or trivial.
* Step: choose safe measurement (only one generator anticommutes).

**Round 2 (medium):**

* Show CZ edges (circuit image). Provide $\langle S'\rangle$ and ask: which $\langle\tilde S\rangle$ results after CZ conjugation?
* Step: choose correct stabilizer generator set (multiple-choice).
* Then choose safe measurement.

**Round 3 (harder):**

* Introduce a small PES: one rotation box, e.g. $X(\theta)$ or $Z(\theta)$.
* Step: choose which Pauli evolution (PES skeleton) is extractable w.r.t offered measurement group.
* (Keep angles hidden—just structural commutation matters.)

**Round 4 (spicy but doable):**

* Give measurement outcome signs $m \in {+1,-1}$.
* Ask player: which correction string $R_{m}$ (Pauli from stabilizer group) should be applied.

You can keep every question as multiple-choice, as you wanted.

---

## 6. Frontend asset conventions

Store everything under:

* `docs/assets/`

Suggested subfolders:

* `docs/assets/slides/`
* `docs/assets/rounds/`
* `docs/assets/info/`

Then JSON references are relative to `assets_base`.

Example:

* `"rounds/r3-circuit.png"` resolves to `docs/assets/rounds/r3-circuit.png`.

---

## 7. Terminal / Atari theme

Implement in `docs/style.css`:

* dark background
* monospace pixel-ish font
* green/amber text

### Font options (no build tooling)

Use a Google-font-like pixel font via CSS `@font-face` (local copy preferred for offline/GitHub stability).

Implementation path:

1. add `docs/assets/fonts/PressStart2P-Regular.ttf` (or similar)
2. in CSS:

```css
@font-face {
  font-family: "PressStart";
  src: url("assets/fonts/PressStart2P-Regular.ttf") format("truetype");
}

:root {
  --bg: #0b0f0c;
  --fg: #c7ffb5;
  --accent: #6aff8f;
  --danger: #ff5f5f;
}

body {
  background: var(--bg);
  color: var(--fg);
  font-family: "PressStart", monospace;
}

button {
  font-family: inherit;
  border: 1px solid var(--accent);
  background: transparent;
  color: var(--fg);
}

button:hover {
  background: rgba(106, 255, 143, 0.15);
}
```

---

## 8. Optional: math rendering

If you want inline LaTeX in prompts/options, easiest static solution is KaTeX.

Two levels:

A) **No library** (fastest): show raw strings like `Z3X4` and keep it readable.

B) **KaTeX auto-render** (still static):

* include KaTeX CSS/JS in `index.html`
* render `$$...$$` and `$...$` inside the injected HTML.

Given your preference for `\ket{}` and `\bra{}` etc: KaTeX supports `braket` macros if included or defined; otherwise define macros.

But: for Secret Santa, simplest is to **avoid math rendering** and keep labels like `Z3 X4`.

---

## 9. Integration workflow (manual rounds now, backend later)

### Now (manual)

1. Edit `docs/levels/level-1.json` to include intro slides + rounds.
2. Put placeholder images in `docs/assets/...`.
3. Run `python -m http.server 8000` and test.

### Next (semi-automated)

1. Write Python helpers in `backend/qc-main0.py` to compute stabilizers and validate.
2. Write `backend/cli_generate.py --validate` to sanity check your JSON.
3. Write `backend/rendering.py` to export PNG circuits from your spec.

---

## 10. Minimal “round spec” format for circuit rendering

To avoid coupling JSON to Stim/Qiskit internals, add an optional `qc_spec` per round:

```json
"qc_spec": {
  "n_qubits": 5,
  "alice_qubits": [0,1,2],
  "bob_qubits": [3,4],
  "cz_edges": [[0,3],[1,3],[2,4]],
  "rotations": [
    {"gate": "X", "q": 1, "theta": "theta1"},
    {"gate": "Z", "q": 3, "theta": "theta2"}
  ],
  "measurements": [
    {"pauli": "Z3 X4", "who": "charlie"}
  ]
}
```

Then renderer can always draw something without needing full simulation.

---

## 11. What Codex should implement (checklist)

### Frontend

* [ ] Update `docs/main.js` to new state machine and schema.
* [ ] Implement `renderHome`, `renderIntro`, `renderInfo`, `renderRound`, `renderGameOver`, `renderVictory`.
* [ ] Implement timer.
* [ ] Implement cheat-code skip.
* [ ] Implement restart game.
* [ ] Ensure asset paths are consistent with `assets_base`.

### Backend

* [ ] Implement validation in `backend/rounds.py`.
* [ ] Add QC helpers in `backend/qc-main0.py`:

  * [ ] Pauli parsing
  * [ ] commutation
  * [ ] CZ conjugation
  * [ ] safe-measurement predicate
* [ ] Add optional rendering hooks in `backend/rendering.py` (even schematic ok).
* [ ] Update `backend/cli_generate.py` to support `--validate` and `--render`.

---

## 12. Sanity tests

### Frontend tests (manual)

* Can start from Home.
* Intro navigation works; Skip works.
* Info page opens and returns.
* Timer expires -> Game Over.
* Correct answer increments stats and enables Next.
* Wrong answer -> Game Over.
* Cheat-code skip works.
* Restart always returns to Home.

### Backend tests

* `--validate` catches missing assets / missing correct option.
* QC checks (optional) warn if a “safe measurement” is actually unsafe under current stabilizers.

---

## 13. Notes on the math ↔ game mapping

The game narrative can say:

* “Your logical info is $\ket{\psi}$ embedded in stabilizer structure $\langle\tilde S\rangle$.”
* “Charlie must measure something; you choose the least destructive measurement.”
* “Later rounds: you identify the extracted unitary (PES skeleton) and the Clifford part, and decide corrections based on outcome.”

Implementation-wise, this is just multiple-choice steps.

That’s it. If Codex implements the schema + state machine, you can fill in the physics in JSON at your own pace.



## Appendix A: Example campaign JSON (drop-in)

Save as: `docs/levels/example-campaign.json` (or rename to `level-1.json`).

Notes:

* Two rounds:

  * Round 1: select measurement (single step)
  * Round 2: select measurement + select correction given an outcome (two steps)
* Image paths are placeholders; create empty PNGs at the referenced locations or update them.
* To keep this drop-in robust, option labels use plain text (no LaTeX rendering required).

```json
{
  "schema_version": "1.0",
  "meta": {
    "title": "Stabilizer Survival",
    "subtitle": "Harold Edition",
    "theme": "terminal",
    "assets_base": "assets"
  },
  "config": {
    "timer": {"enabled": true, "seconds_per_step": 30},
    "cheat": {"enabled": true, "code": "HAROLD"}
  },
  "info": {
    "markdown": "# Rulebook

- You are Alice. Protect psi inside a stabilizer backbone.
- Bob entangles with CZ and sometimes inserts Pauli-rotations.
- Charlie must measure something: you choose the least destructive option.
- Later rounds: recover the induced unitary/byproduct.
",
    "images": ["info/rulebook.png"]
  },
  "intro_slides": [
    {
      "id": "intro-1",
      "title": "Your code is under attack",
      "body_markdown": "Bob entangles his + ancillas with your system, then Charlie measures.",
      "images": ["slides/intro-1.png"]
    },
    {
      "id": "intro-2",
      "title": "How to win",
      "body_markdown": "Pick answers that keep the process deterministic: no logical measurement; apply the correct byproduct when asked.",
      "images": ["slides/intro-2.png"]
    }
  ],
  "rounds": [
    {
      "id": "r1",
      "title": "Round 1: Pick a non-destructive measurement",
      "difficulty": 1,
      "context_markdown": "Alice holds (S, psi). Bob uses only CZ. Charlie offers Pauli measurements.",
      "assets": {
        "circuit_image": "rounds/r1-circuit.png",
        "graph_image": "rounds/r1-graph.png"
      },
      "qc_spec": {
        "n_qubits": 5,
        "alice_qubits": [0, 1, 2],
        "bob_qubits": [3, 4],
        "cz_edges": [[1, 3], [2, 4]],
        "rotations": [],
        "measurements": []
      },
      "steps": [
        {
          "id": "r1-s1",
          "kind": "select_measurement",
          "prompt_markdown": "Charlie offers these measurements. Pick the one that is non-destructive.",
          "options": [
            {"id": "A", "label": "Z3 X4", "detail_markdown": "Candidate 1"},
            {"id": "B", "label": "X1 Z3", "detail_markdown": "Candidate 2"},
            {"id": "C", "label": "Z1 Z2", "detail_markdown": "Candidate 3"}
          ],
          "answer": {"correct_option_id": "A"},
          "feedback": {
            "on_correct_markdown": "Correct. This preserves recoverability.",
            "on_wrong_markdown": "Wrong. This destroys logical info (or breaks determinism)."
          },
          "timer": {"enabled": true, "seconds": 25}
        }
      ]
    },
    {
      "id": "r2",
      "title": "Round 2: Outcome-dependent correction",
      "difficulty": 2,
      "context_markdown": "Charlie measures your chosen M and obtains an outcome. Pick the correct byproduct correction.",
      "assets": {
        "circuit_image": "rounds/r2-circuit.png",
        "graph_image": "rounds/r2-graph.png"
      },
      "qc_spec": {
        "n_qubits": 5,
        "alice_qubits": [0, 1, 2],
        "bob_qubits": [3, 4],
        "cz_edges": [[1, 3], [2, 4]],
        "rotations": [{"gate": "X", "q": 1, "theta": "theta1"}],
        "measurements": [{"pauli": "Z3 X4", "who": "charlie"}]
      },
      "steps": [
        {
          "id": "r2-s1",
          "kind": "select_measurement",
          "prompt_markdown": "Pick a measurement that keeps the PES extractable.",
          "options": [
            {"id": "A", "label": "Z3 X4"},
            {"id": "B", "label": "X1 Z3"},
            {"id": "C", "label": "X3"}
          ],
          "answer": {"correct_option_id": "A"},
          "feedback": {
            "on_correct_markdown": "Good. Now handle the outcome.",
            "on_wrong_markdown": "Bad measurement choice."
          },
          "timer": {"enabled": true, "seconds": 30}
        },
        {
          "id": "r2-s2",
          "kind": "select_correction",
          "prompt_markdown": "Outcome revealed: m = -1. Which correction should Alice apply?",
          "options": [
            {"id": "A", "label": "I"},
            {"id": "B", "label": "X1"},
            {"id": "C", "label": "Z0 Z2"}
          ],
          "answer": {"correct_option_id": "B"},
          "feedback": {
            "on_correct_markdown": "Recovered. Determinism restored.",
            "on_wrong_markdown": "Wrong byproduct; computation deviates."
          },
          "timer": {"enabled": true, "seconds": 25}
        }
      ]
    }
  ]
}
```

Implementation note (frontend):

* Treat `qc_spec` as optional (ignore unless you want to render extra hints).
* The game only needs `steps[*].options` and `steps[*].answer.correct_option_id` to run.
