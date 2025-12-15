# Intro slides + in-game Rules/Hints content

This note is a drop-in content plan (copy + JSON + implementation instructions) for the website intro slides and the in-game Rules/Hints overlay.

It assumes the current frontend loads `docs/levels/level-1.json` and starts slides via `showSlides(level1Data.introSlides, onSlidesDone)` as in the repo digest. fileciteturn9file1

---

## A. Slide deck content (Level 1)

### Slide schema (keep it simple)

Use the existing array `introSlides: [{ title, text, imageSrc?, imageAlt? }, ...]` in `docs/levels/level-1.json`. The current code already checks `level1Data.introSlides.length`. fileciteturn9file1

Add `imageSrc` only when you actually have a PNG/GIF.

### Suggested slide copy

Paste this into `docs/levels/level-1.json` under `introSlides` (replace the dummy ones).

```json
[
  {
    "title": "Stabilizer Survival: The Kingdom State",
    "text": "Alice stores her kingdom’s secret in an encoded quantum state $\\ket{\\mathcal{S},\\psi}$.\\n\\n- $\\braket{\\mathcal{S}}$ are the stabilizers: the castle walls.\\n- $\\ket{\\psi}$ is the logical information: the crown jewels."
  },
  {
    "title": "The Attack",
    "text": "Bob can’t read Alice’s secret directly, so he tries the next best thing:\\n\\n1) entangle his ancillas to Alice (mostly CZ connections), then\\n2) force Charlie to measure some Pauli string(s).\\n\\nMeasurement is irreversible. If the wrong Pauli gets measured, Alice’s logical state can be damaged."
  },
  {
    "title": "The Twist",
    "text": "Stabilizers are NOT public.\\n\\n- Bob does not know $\\mathcal{S}$.\\n- Charlie does not know $\\mathcal{S}$.\\n- Only Alice knows $\\mathcal{S}$ — and she shows it to YOU.\\n\\nSo you’re playing with privileged information, like a proper cryptographer."
  },
  {
    "title": "What You See Each Round",
    "text": "Each round shows:\\n\\n- Alice’s current stabilizer generators (what she knows).\\n- A circuit sketch of Bob’s CZ-attack + Charlie’s measurement stage.\\n- A shortlist of candidate Pauli measurements Charlie might be forced to do.\\n\\nYour job: pick which measurement Alice should *encourage* Charlie to perform."
  },
  {
    "title": "Level 1 Rule (Non-destructive measurement)",
    "text": "A candidate measurement $M$ is *safe* if it does NOT act like a logical measurement on $\\ket{\\psi}$.\\n\\nOperational rule for the puzzle: a measurement that only ‘updates the stabilizer record’ is allowed; a measurement that reveals logical info is game-over.\\n\\nDuring play, use the Hints panel for the quick checklist."
  },
  {
    "title": "UI Navigation",
    "text": "Buttons you’ll have:\\n\\n- Prev / Next: step through story slides.\\n- Skip: jump straight to the first round.\\n- Start Level 1: begin the game.\\n\\nIn-game:\\n- Rules: opens the full story + mechanics reference.\\n- Hints: opens the short ‘how to decide’ checklist.\\n- Restart Game: resets everything back to the intro."
  },
  {
    "title": "Timer + Win Condition",
    "text": "Each round has a timer. If it hits zero: game over.\\n\\nIf you select a safe option: you survive the round and can click Next Round.\\n\\nLater rounds may ask extra questions (identify $U_{\\mathrm{PES}}$, identify the extracted Clifford, incorporate measurement outcomes)."
  }
]
```

Notes:

* I used inline LaTeX strings (escaped) in `text`. If your current slide renderer is plain-text only, it will show the `$...$` literally; that’s fine for now, or you can add a very small math renderer later.

---

## B. In-game Rules/Hints overlay content

Right now the UI uses a `rulesBtn` and `showInfoOverlay()` / `hideInfoOverlay()` hooks. fileciteturn9file1

### Desired behavior

* Two buttons visible during gameplay:

  * **Rules**: full reference (story + mechanics)
  * **Hints**: short checklist (fast to read during the timer)
* Both open the same overlay container, but with different tabs/sections selected.

### Content blocks (Markdown-like plain text)

Put these as string constants in `docs/js/main.js` (or load from files if you prefer).

#### Rules (long)

```
STORY
- Alice encodes her secret in |S, ψ⟩.
- Bob tries to damage ψ using entanglement + forced Pauli measurements.
- Charlie is a spy: she sends Alice a shortlist of possible measurements she might be forced to perform.
- Stabilizers are secret: only Alice knows S (and she shows it to you).

MECHANICS
- Each round: choose an option (measurement, or sometimes an extracted unitary, etc.).
- If time runs out: you lose the round.
- If you pick a destructive option: you lose immediately.

WHAT COUNTS AS 'DESTRUCTIVE'
- A measurement is destructive if it effectively measures logical information (acts like a logical Pauli on ψ).
- A measurement is safe if it only changes the stabilizer record (i.e., it is absorbed by stabilizer update / correction logic).

LEVEL 2 (later)
- Bob introduces non-Clifford Pauli evolutions U_PES(θ).
- You must choose measurements that keep the instance extractable AND identify what unitary was induced so Alice can invert it.
```

#### Hints (short)

```
QUICK CHECKLIST (Level 1)
1) Look at the candidate measurement M.
2) Ask: does M behave like a stabilizer-only disturbance, or does it look logical?
3) Prefer measurements that 'hit' exactly one stabilizer generator (so one generator is replaced/updated) rather than measurements that commute with everything or look like a logical operator.

RULE OF THUMB
- “Commutes with all stabilizers” is suspicious (often logical).
- “Anticommutes with a stabilizer generator” is usually salvageable (stabilizer update).

If you’re unsure: choose the option that is most obviously tied to the stabilizer subsystem rather than the logical subsystem.
```

(You can tighten these later once you finalize the exact correctness predicate used in your rounds.)

---

## C. Implementation instructions for the local coding agent

### C.1. Where to edit slides

Slides are currently data-driven from `docs/levels/level-1.json` under `introSlides`. The JS checks `level1Data.introSlides` and calls `showSlides(...)`. fileciteturn9file1turn9file16

Action:

1. Edit `docs/levels/level-1.json` and replace the `introSlides` array with the one in Section A.
2. Ensure the JSON remains valid.

### C.2. Make slides easy to edit later (recommended change)

Problem: editing long strings inside JSON is annoying.

Recommended refactor (minimal): allow each slide to reference an external text file.

**New slide fields**:

* `textPath`: e.g. `"docs/content/slides/intro-01.txt"` (or relative `"content/slides/intro-01.txt"` if you fetch relative to `/docs/`)

**Agent tasks**:

1. Create directory: `docs/content/slides/`.
2. Create files:

   * `intro-01.txt`, `intro-02.txt`, ... each containing the slide `text`.
3. In `docs/levels/level-1.json`, replace `text` with `textPath`.
4. Update `showSlides(slides, done)` to:

   * if `slide.textPath` exists, fetch it (once) and cache it.
   * render the fetched text.

Pseudo-code:

```js
const slideTextCache = new Map();

async function getSlideText(slide) {
  if (slide.text) return slide.text;
  if (!slide.textPath) return "";

  if (slideTextCache.has(slide.textPath)) return slideTextCache.get(slide.textPath);
  const resp = await fetch(slide.textPath);
  const txt = await resp.text();
  slideTextCache.set(slide.textPath, txt);
  return txt;
}

async function renderSlide(i) {
  const slide = currentSlides[i];
  slideTitleEl.textContent = slide.title;
  slideBodyEl.textContent = await getSlideText(slide);
  // image optional
}
```

This keeps content editable as plain files, without requiring any JS knowledge for routine copy edits.

### C.3. Add a “Hints” button during gameplay

The repo already wires `rulesBtn` to `showInfoOverlay()` and `infoCloseBtn` to `hideInfoOverlay()`. fileciteturn9file1turn9file2

Agent tasks:

1. In `docs/index.html` (or the main HTML), add a new button with id `hints-btn` near `rules-btn`.
2. In `docs/js/main.js`, wire it similarly:

```js
const hintsBtn = $("#hints-btn");
if (hintsBtn) {
  hintsBtn.addEventListener("click", () => showInfoOverlay("hints"));
}
```

3. Modify `showInfoOverlay(mode)` so that:

   * when `mode === "rules"` (default), display the Rules block
   * when `mode === "hints"`, display the Hints block

Simple approach: one overlay, two `<div>` sections, hide/show with `.hidden`.

### C.4. “Rules/Hints always available” requirement

Ensure the overlay elements are outside the slides container and outside per-round render logic, so they persist while playing.

### C.5. Stabilizers are secret requirement

Do **not** display stabilizers in any “Charlie/Bob” panels.

Concretely:

* Only show stabilizers in Alice’s panel (the player view).
* Charlie’s panel should only show the candidate measurement options list.

(That matches your narrative constraint: only Alice knows $\mathcal{S}$.)

---

## D. Optional: visuals in slides

When you are ready:

* Put PNG/GIF assets under `docs/assets/images/`.
* Add `imageSrc: "assets/images/your-file.png"` to any slide.

This avoids 404s like the current missing `level-1-round1-*.png` referenced earlier in the console. fileciteturn9file1

---

## E. Next step

After the agent implements Section C, you can iteratively refine:

* story tone,
* the precise correctness predicate (logical vs non-logical),
* and the per-round presentation.
