#!/usr/bin/env bash
set -e

PROJECT_DIR="stabmbqc-game"

if [ ! -d "$PROJECT_DIR/docs" ]; then
  echo "Could not find $PROJECT_DIR/docs. Run this script from the parent directory of stabmbqc-game."
  exit 1
fi

cd "$PROJECT_DIR"

mkdir -p docs/levels
mkdir -p docs/assets

echo "Updating docs/index.html..."
cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Stabilizer Survival – Level 1</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Slides overlay (intro / between levels) -->
  <div id="slides-overlay">
    <div id="slides-content">
      <h1 id="slide-title"></h1>
      <div id="slide-main">
        <div id="slide-text"></div>
        <div id="slide-media">
          <img id="slide-circuit" alt="Circuit" />
          <img id="slide-graph" alt="Graph" />
        </div>
      </div>
      <div id="slides-controls">
        <button id="slide-prev-btn" class="secondary-btn">⮜ Back</button>
        <button id="slide-next-btn" class="secondary-btn">Next ⮞</button>
        <button id="slide-start-level-btn" class="primary-btn" style="display:none;">
          Start level
        </button>
      </div>
    </div>
  </div>

  <!-- Game container -->
  <div id="game-container" class="hidden">
    <header id="game-header">
      <div>
        <h1 id="game-title">Stabilizer Survival</h1>
        <div id="game-level">Loading level...</div>
        <div id="round-label"></div>
      </div>
      <div id="header-right">
        <div id="round-progress"></div>
        <div id="timer-box">
          Time left: <span id="timer-value">--</span>s
        </div>
      </div>
    </header>

    <main id="game-main">
      <section id="left-panel">
        <div id="graph-wrapper">
          <img id="graph-image" alt="Code graph" />
        </div>
        <div id="circuit-box">
          <h2>Circuit view</h2>
          <div id="circuit-wrapper">
            <img id="circuit-image" alt="Circuit diagram" />
          </div>
        </div>
        <div id="stabilizer-box">
          <h2>Stabilizers</h2>
          <ul id="stabilizer-list"></ul>
        </div>
      </section>

      <section id="right-panel">
        <div id="description-box">
          <p id="level-description"></p>
          <p id="round-text" class="round-text"></p>
        </div>

        <div id="choices-box">
          <h2>Charlie’s possible measurements</h2>
          <div id="candidate-buttons"></div>
        </div>

        <div id="feedback-box">
          <p id="feedback-message"></p>
        </div>

        <div id="controls-box">
          <button id="next-round-btn" class="secondary-btn" style="display:none;">
            Next round ⮞
          </button>
          <button id="restart-level-btn" class="secondary-btn" style="display:none;">
            Restart level ↻
          </button>
          <button id="next-level-btn" class="primary-btn" style="display:none;">
            Level 2 (coming soon)
          </button>
        </div>
      </section>
    </main>
  </div>

  <script src="main.js" defer></script>
</body>
</html>
EOF

echo "Updating docs/style.css..."
cat > docs/style.css << 'EOF'
/* Basic layout */

body {
  margin: 0;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: #0b1020;
  color: #f5f5f5;
}

.hidden {
  display: none !important;
}

#game-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}

#game-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

#game-title {
  margin: 0;
  font-size: 1.8rem;
}

#game-level {
  font-size: 0.95rem;
  color: #c5c5ff;
}

#round-label {
  font-size: 0.9rem;
  color: #9ca3ff;
  margin-top: 4px;
}

#header-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

#round-progress {
  font-size: 0.85rem;
  color: #c5c5ff;
}

#timer-box {
  font-size: 0.85rem;
  color: #f97373;
}

/* Main layout */

#game-main {
  display: grid;
  grid-template-columns: 1.1fr 1.4fr;
  gap: 16px;
}

/* Left panel */

#left-panel {
  background: #151a30;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 0 10px rgba(0,0,0,0.35);
}

#graph-wrapper {
  background: #0f1425;
  border-radius: 8px;
  padding: 8px;
  text-align: center;
  margin-bottom: 12px;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

#graph-image {
  max-width: 100%;
  max-height: 200px;
  object-fit: contain;
}

#circuit-box {
  background: #0f1425;
  border-radius: 8px;
  padding: 8px 10px;
  margin-bottom: 12px;
}

#circuit-box h2 {
  margin: 0 0 6px 0;
  font-size: 1rem;
}

#circuit-wrapper {
  text-align: center;
}

#circuit-image {
  max-width: 100%;
  max-height: 180px;
  object-fit: contain;
}

#stabilizer-box h2 {
  margin-top: 0;
  margin-bottom: 4px;
  font-size: 1rem;
}

#stabilizer-list {
  list-style: none;
  padding-left: 0;
  margin: 0;
}

#stabilizer-list li {
  background: #1d2340;
  margin-bottom: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 0.9rem;
}

/* Right panel */

#right-panel {
  background: #151a30;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 0 10px rgba(0,0,0,0.35);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

#description-box {
  background: #0f1425;
  padding: 8px 10px;
  border-radius: 6px;
  font-size: 0.95rem;
}

.round-text {
  margin-top: 8px;
  font-size: 0.9rem;
  color: #d1d5ff;
}

#choices-box h2 {
  margin-top: 0;
  margin-bottom: 6px;
  font-size: 1rem;
}

#candidate-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Candidate buttons */

.candidate-btn {
  border: 1px solid #444b80;
  background: #111633;
  color: #f5f5f5;
  padding: 8px 10px;
  border-radius: 6px;
  font-family: "JetBrains Mono", "Fira Code", monospace;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.1s ease, opacity 0.1s ease;
}

.candidate-btn:hover:not(.disabled) {
  background: #1e2654;
  box-shadow: 0 0 8px rgba(70, 104, 255, 0.4);
  transform: translateY(-1px);
}

.candidate-btn:active:not(.disabled) {
  transform: translateY(1px);
}

.candidate-btn.disabled {
  opacity: 0.45;
  cursor: default;
}

/* Feedback */

#feedback-box {
  min-height: 40px;
  display: flex;
  align-items: center;
}

#feedback-message {
  margin: 0;
  font-size: 0.95rem;
}

.feedback-safe {
  color: #7cffb8;
}

.feedback-unsafe {
  color: #ff7a7a;
}

/* Shake animation for bad choice */

.shake {
  animation: shake 0.25s linear;
}

@keyframes shake {
  0%   { transform: translateX(0); }
  25%  { transform: translateX(-4px); }
  50%  { transform: translateX(4px); }
  75%  { transform: translateX(-2px); }
  100% { transform: translateX(0); }
}

/* Controls */

#controls-box {
  margin-top: auto;
  text-align: right;
}

#next-round-btn,
#restart-level-btn,
#next-level-btn {
  padding: 6px 10px;
  border-radius: 6px;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
}

#next-round-btn {
  background: #22c55e;
  color: #041016;
  margin-right: 8px;
}

#next-round-btn:hover {
  background: #16a34a;
}

#restart-level-btn {
  background: #f97316;
  color: #041016;
  margin-right: 8px;
}

#restart-level-btn:hover {
  background: #ea580c;
}

#next-level-btn {
  background: #3b82f6;
  color: white;
}

#next-level-btn:hover {
  background: #2563eb;
}

/* Slides overlay */

#slides-overlay {
  position: fixed;
  inset: 0;
  background: radial-gradient(circle at top, #1e293b 0, #020617 55%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

#slides-content {
  max-width: 800px;
  width: 90%;
  background: rgba(15, 23, 42, 0.97);
  border-radius: 12px;
  padding: 20px 22px;
  box-shadow: 0 0 30px rgba(0,0,0,0.6);
}

#slides-content h1 {
  margin-top: 0;
  margin-bottom: 12px;
}

#slide-main {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 12px;
  margin-bottom: 12px;
}

#slide-text {
  font-size: 0.95rem;
  line-height: 1.4;
}

#slide-media {
  text-align: center;
}

#slide-media img {
  max-width: 100%;
  max-height: 160px;
  object-fit: contain;
  margin-bottom: 4px;
}

#slides-controls {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

/* Buttons used in slides */

.primary-btn {
  padding: 6px 14px;
  border-radius: 8px;
  border: none;
  background: #4f46e5;
  color: #f9fafb;
  font-size: 0.95rem;
  cursor: pointer;
}

.primary-btn:hover {
  background: #4338ca;
}

.secondary-btn {
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid #4b5563;
  background: #111827;
  color: #f9fafb;
  font-size: 0.9rem;
  cursor: pointer;
}

.secondary-btn:hover {
  background: #1f2937;
}

/* Small screens */

@media (max-width: 800px) {
  #game-main {
    grid-template-columns: 1fr;
  }

  #slide-main {
    grid-template-columns: 1fr;
  }
}
EOF

echo "Updating docs/main.js..."
cat > docs/main.js << 'EOF'
// ==========================
// Utility: Pauli commutation
// ==========================

// Given two single-qubit Paulis a,b in {I,X,Y,Z}, do they anticommute?
function singleAnticommute(a, b) {
  if (a === 'I' || b === 'I' || a === b) {
    return false;
  }
  // X, Y, Z anticommute whenever they are different non-I Paulis
  return true;
}

// Given two Pauli strings over {I,X,Y,Z}, decide if they anticommute.
// They anticommute iff the number of positions with singleAnticommute(a,b) is odd.
function paulisAnticommute(p1, p2) {
  if (p1.length !== p2.length) {
    throw new Error("Pauli strings must have same length");
  }
  let count = 0;
  for (let i = 0; i < p1.length; i++) {
    if (singleAnticommute(p1[i], p2[i])) {
      count += 1;
    }
  }
  return (count % 2) === 1;
}

// Check if a candidate measurement M is safe given a list of stabilizer generators.
// Rule (Level 1): safe iff M anticommutes with at least one stabilizer generator.
function isSafeMeasurement(candidatePauli, stabilizers) {
  for (const S of stabilizers) {
    if (paulisAnticommute(candidatePauli, S)) {
      return true;
    }
  }
  return false;
}

// ==========================
// DOM helpers & game state
// ==========================

function $(selector) {
  return document.querySelector(selector);
}

let currentLevel = null;
let currentRoundIndex = 0;
let hasAnsweredThisRound = false;

// slides state
let currentSlides = [];
let currentSlideIndex = 0;
let slidesDoneCallback = null;

// timer state
let roundTimerId = null;
let remainingSeconds = 0;

// ==========================
// Level loading
// ==========================

async function loadLevel(levelId) {
  const response = await fetch(`levels/${levelId}.json`);
  if (!response.ok) {
    throw new Error(`Could not load level file for ${levelId}`);
  }
  const levelData = await response.json();
  return levelData;
}

// ==========================
// Slides engine
// ==========================

function showSlides(slides, onDone) {
  currentSlides = slides || [];
  currentSlideIndex = 0;
  slidesDoneCallback = typeof onDone === "function" ? onDone : null;

  const overlay = $("#slides-overlay");
  if (overlay) overlay.classList.remove("hidden");

  renderSlide();
}

function hideSlides() {
  const overlay = $("#slides-overlay");
  if (overlay) overlay.classList.add("hidden");
}

function renderSlide() {
  if (!currentSlides || currentSlides.length === 0) {
    // nothing to show
    hideSlides();
    if (slidesDoneCallback) slidesDoneCallback();
    return;
  }

  const slide = currentSlides[currentSlideIndex];

  const titleEl = $("#slide-title");
  const textEl = $("#slide-text");
  const circImg = $("#slide-circuit");
  const graphImg = $("#slide-graph");
  const prevBtn = $("#slide-prev-btn");
  const nextBtn = $("#slide-next-btn");
  const startBtn = $("#slide-start-level-btn");

  if (titleEl) titleEl.textContent = slide.title || "";
  if (textEl) textEl.textContent = slide.text || "";

  if (circImg) {
    if (slide.circuitImage) {
      circImg.src = slide.circuitImage;
      circImg.style.display = "block";
    } else {
      circImg.style.display = "none";
    }
  }

  if (graphImg) {
    if (slide.graphImage) {
      graphImg.src = slide.graphImage;
      graphImg.style.display = "block";
    } else {
      graphImg.style.display = "none";
    }
  }

  const atFirst = currentSlideIndex === 0;
  const atLast = currentSlideIndex === currentSlides.length - 1;

  if (prevBtn) prevBtn.disabled = atFirst;
  if (nextBtn) nextBtn.style.display = atLast ? "none" : "inline-block";
  if (startBtn) startBtn.style.display = atLast ? "inline-block" : "none";
}

function nextSlide() {
  if (!currentSlides || currentSlides.length === 0) return;
  if (currentSlideIndex < currentSlides.length - 1) {
    currentSlideIndex += 1;
    renderSlide();
  } else {
    // done
    hideSlides();
    if (slidesDoneCallback) slidesDoneCallback();
  }
}

function prevSlide() {
  if (!currentSlides || currentSlides.length === 0) return;
  if (currentSlideIndex > 0) {
    currentSlideIndex -= 1;
    renderSlide();
  }
}

// ==========================
// Round timer
// ==========================

function clearRoundTimer() {
  if (roundTimerId !== null) {
    clearInterval(roundTimerId);
    roundTimerId = null;
  }
}

function startRoundTimer(limitSeconds) {
  clearRoundTimer();

  const timerValueEl = $("#timer-value");
  if (!timerValueEl || !limitSeconds) {
    return;
  }

  remainingSeconds = limitSeconds;
  timerValueEl.textContent = remainingSeconds.toString();

  roundTimerId = setInterval(() => {
    remainingSeconds -= 1;
    if (remainingSeconds <= 0) {
      remainingSeconds = 0;
    }
    timerValueEl.textContent = remainingSeconds.toString();

    if (remainingSeconds <= 0) {
      clearRoundTimer();
      if (!hasAnsweredThisRound) {
        handleTimeExpired();
      }
    }
  }, 1000);
}

function handleTimeExpired() {
  hasAnsweredThisRound = true;
  disableCandidateButtons();

  const feedback = $("#feedback-message");
  if (feedback) {
    feedback.textContent = "⏰ Time's up! The hacker gets through this round. Game over for this level.";
    feedback.className = "feedback-unsafe";
  }

  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");
  const restartBtn = $("#restart-level-btn");
  if (nextRoundBtn) nextRoundBtn.style.display = "none";
  if (nextLevelBtn) nextLevelBtn.style.display = "none";
  if (restartBtn) restartBtn.style.display = "inline-block";
}

// ==========================
// Game rendering
// ==========================

function renderLevel(level) {
  currentLevel = level;
  currentRoundIndex = 0;

  const levelTitleEl = $("#game-level");
  const levelDescEl = $("#level-description");
  const progressEl = $("#round-progress");

  if (levelTitleEl) levelTitleEl.textContent = level.title || "Unknown level";
  if (levelDescEl) levelDescEl.textContent = level.description || "";
  if (progressEl) {
    progressEl.textContent = `Round ${currentRoundIndex + 1} of ${level.rounds.length}`;
  }

  renderRound();
}

function renderRound() {
  const level = currentLevel;
  if (!level) return;

  const round = level.rounds[currentRoundIndex];

  hasAnsweredThisRound = false;

  const feedbackEl = $("#feedback-message");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");
  const restartBtn = $("#restart-level-btn");
  const roundLabelEl = $("#round-label");
  const roundTextEl = $("#round-text");
  const progressEl = $("#round-progress");
  const graphImg = $("#graph-image");
  const circImg = $("#circuit-image");
  const stabilizerList = $("#stabilizer-list");
  const buttonsDiv = $("#candidate-buttons");
  const leftPanel = $("#left-panel");
  const timerValueEl = $("#timer-value");

  if (feedbackEl) {
    feedbackEl.textContent = "";
    feedbackEl.className = "";
  }
  if (nextRoundBtn) nextRoundBtn.style.display = "none";
  if (nextLevelBtn) nextLevelBtn.style.display = "none";
  if (restartBtn) restartBtn.style.display = "none";
  if (timerValueEl) timerValueEl.textContent = "--";

  if (roundLabelEl) roundLabelEl.textContent = round.label || `Round ${currentRoundIndex + 1}`;
  if (roundTextEl) roundTextEl.textContent = round.text || "";

  if (progressEl) {
    progressEl.textContent = `Round ${currentRoundIndex + 1} of ${level.rounds.length}`;
  }

  if (graphImg) {
    if (round.graphImage) {
      graphImg.src = round.graphImage;
      graphImg.style.display = "block";
    } else {
      graphImg.style.display = "none";
    }
  }

  if (circImg) {
    if (round.circuitImage) {
      circImg.src = round.circuitImage;
      circImg.style.display = "block";
    } else {
      circImg.style.display = "none";
    }
  }

  if (stabilizerList) {
    stabilizerList.innerHTML = "";
    round.stabilizers.forEach((S, idx) => {
      const li = document.createElement("li");
      li.textContent = `S${idx + 1} = ${S}`;
      stabilizerList.appendChild(li);
    });
  }

  if (buttonsDiv) {
    buttonsDiv.innerHTML = "";
    if (leftPanel) leftPanel.classList.remove("shake");

    round.candidates.forEach((cand) => {
      const btn = document.createElement("button");
      btn.className = "candidate-btn";
      btn.textContent = cand.label;
      btn.addEventListener("click", () => {
        handleCandidateClick(cand, round);
      });
      buttonsDiv.appendChild(btn);
    });
  }

  // start timer for this round
  const limit = level.roundTimeLimitSeconds || 0;
  startRoundTimer(limit);
}

function disableCandidateButtons() {
  const btns = document.querySelectorAll(".candidate-btn");
  btns.forEach((b) => {
    b.classList.add("disabled");
    b.disabled = true;
  });
}

function handleCandidateClick(candidate, round) {
  if (hasAnsweredThisRound) return;

  const pauli = candidate.pauli;
  const stabs = round.stabilizers;
  const safe = isSafeMeasurement(pauli, stabs);

  const feedback = $("#feedback-message");
  const leftPanel = $("#left-panel");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");
  const restartBtn = $("#restart-level-btn");
  const timerValueEl = $("#timer-value");

  clearRoundTimer();
  if (timerValueEl) timerValueEl.textContent = "--";

  if (safe) {
    if (feedback) {
      feedback.textContent = `✅ Safe: ${candidate.label} anticommutes with at least one stabilizer generator, so it only updates the stabilizer and leaves the logical info intact.`;
      feedback.className = "feedback-safe";
    }
    disableCandidateButtons();
    hasAnsweredThisRound = true;

    const isLastRound = currentRoundIndex === currentLevel.rounds.length - 1;
    if (isLastRound) {
      if (nextLevelBtn) nextLevelBtn.style.display = "inline-block";
    } else {
      if (nextRoundBtn) nextRoundBtn.style.display = "inline-block";
    }
  } else {
    if (feedback) {
      feedback.textContent = `❌ Unsafe: ${candidate.label} commutes with all stabilizers in this toy level, so we treat it as measuring a logical operator. The logical qubit collapses – game over.`;
      feedback.className = "feedback-unsafe";
    }
    if (leftPanel) {
      leftPanel.classList.remove("shake");
      void leftPanel.offsetWidth; // restart animation
      leftPanel.classList.add("shake");
    }
    disableCandidateButtons();
    hasAnsweredThisRound = true;

    if (nextRoundBtn) nextRoundBtn.style.display = "none";
    if (nextLevelBtn) nextLevelBtn.style.display = "none";
    if (restartBtn) restartBtn.style.display = "inline-block";
  }
}

function goToNextRound() {
  if (!currentLevel) return;
  if (currentRoundIndex < currentLevel.rounds.length - 1) {
    currentRoundIndex += 1;
    renderRound();
  }
}

function restartLevel() {
  if (!currentLevel) return;
  currentRoundIndex = 0;
  renderLevel(currentLevel);
}

// ==========================
// Initialization
// ==========================

window.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM fully loaded, setting up...");

  const slidesPrevBtn = $("#slide-prev-btn");
  const slidesNextBtn = $("#slide-next-btn");
  const slidesStartBtn = $("#slide-start-level-btn");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");
  const restartBtn = $("#restart-level-btn");
  const gameContainer = $("#game-container");

  if (slidesPrevBtn) {
    slidesPrevBtn.addEventListener("click", () => {
      prevSlide();
    });
  }

  if (slidesNextBtn) {
    slidesNextBtn.addEventListener("click", () => {
      nextSlide();
    });
  }

  if (slidesStartBtn) {
    slidesStartBtn.addEventListener("click", () => {
      // finishing slides explicitly from button
      hideSlides();
      if (slidesDoneCallback) slidesDoneCallback();
    });
  }

  if (nextRoundBtn) {
    nextRoundBtn.addEventListener("click", () => {
      goToNextRound();
    });
  }

  if (nextLevelBtn) {
    nextLevelBtn.addEventListener("click", () => {
      alert("Level 2 will add Bob's entangling unitaries and extractability. (Dummy placeholder for now.)");
    });
  }

  if (restartBtn) {
    restartBtn.addEventListener("click", () => {
      restartLevel();
    });
  }

  try {
    const level = await loadLevel("level-1");
    // show slides first, then start the level
    const onSlidesDone = () => {
      if (gameContainer) gameContainer.classList.remove("hidden");
      renderLevel(level);
    };
    if (level.introSlides && level.introSlides.length > 0) {
      showSlides(level.introSlides, onSlidesDone);
    } else {
      hideSlides();
      onSlidesDone();
    }
  } catch (err) {
    console.error("Error loading level:", err);
    if (gameContainer) gameContainer.classList.remove("hidden");
    const levelTitleEl = $("#game-level");
    const levelDescEl = $("#level-description");
    if (levelTitleEl) levelTitleEl.textContent = "Error loading level";
    if (levelDescEl) levelDescEl.textContent = String(err);
  }
});
EOF

echo "Updating docs/levels/level-1.json..."
cat > docs/levels/level-1.json << 'EOF'
{
  "id": "level-1",
  "title": "Level 1 – Don’t Measure the Logical Qubit",
  "description": "Dummy Level 1: in each round, Charlie offers some Pauli measurements on Alice's code. Your job: pick a measurement that is safe – it should anticommute with at least one stabilizer generator, so that it only updates the stabilizer and not the logical information.",
  "roundTimeLimitSeconds": 15,
  "introSlides": [
    {
      "title": "Welcome to Stabilizer Survival",
      "text": "Alice rules a tiny quantum kingdom encoded as |S, ψ⟩. The walls of her castle are the stabilizers; the logical qubit is the throne she wants to protect."
    },
    {
      "title": "The Measurement Hacker",
      "text": "Bob hires a hacker who can only touch the kingdom via Pauli measurements. Some measurements merely swap or flip walls; others smash directly into the throne."
    },
    {
      "title": "Level 1 Rules (Dummy)",
      "text": "In each round, you will see a small stabilizer code and several Pauli measurement options. Choose one that anticommutes with at least one stabilizer generator. Answer in time, and you survive the round."
    }
  ],
  "rounds": [
    {
      "id": 1,
      "label": "Round 1",
      "text": "Dummy round 1: simple 3-qubit code. Only one choice is safe.",
      "numQubits": 3,
      "stabilizers": ["ZZI", "IZZ"],
      "candidates": [
        { "label": "Z I I", "pauli": "ZII" },
        { "label": "X I I", "pauli": "XII" },
        { "label": "X X X", "pauli": "XXX" }
      ]
    },
    {
      "id": 2,
      "label": "Round 2",
      "text": "Dummy round 2: same code, different options.",
      "numQubits": 3,
      "stabilizers": ["ZZI", "IZZ"],
      "candidates": [
        { "label": "I Z I", "pauli": "IZI" },
        { "label": "I X I", "pauli": "IXI" },
        { "label": "Z Z Z", "pauli": "ZZZ" }
      ]
    },
    {
      "id": 3,
      "label": "Round 3",
      "text": "Dummy round 3: one last test. Think about which operators are more likely to be logical.",
      "numQubits": 3,
      "stabilizers": ["ZZI", "IZZ"],
      "candidates": [
        { "label": "I I Z", "pauli": "IIZ" },
        { "label": "X X I", "pauli": "XXI" },
        { "label": "X X X", "pauli": "XXX" }
      ]
    }
  ]
}
EOF

echo "Done. Now run:"
echo "  cd $PROJECT_DIR"
echo "  python -m http.server 8000"
echo "and open http://localhost:8000/docs/ in your browser."
EOF

---

## 2. How to use it

From the folder **above** `stabmbqc-game/`:

```bash
chmod +x update_stabmbqc_game_slides.sh
./update_stabmbqc_game_slides.sh
