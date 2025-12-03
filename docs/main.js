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

// ==========================
// Level loading & rendering
// ==========================

async function loadLevel(levelId) {
  const response = await fetch(`levels/${levelId}.json`);
  if (!response.ok) {
    throw new Error(`Could not load level file for ${levelId}`);
  }
  const levelData = await response.json();
  return levelData;
}

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
  const roundLabelEl = $("#round-label");
  const roundTextEl = $("#round-text");
  const progressEl = $("#round-progress");
  const graphImg = $("#graph-image");
  const circImg = $("#circuit-image");
  const stabilizerList = $("#stabilizer-list");
  const buttonsDiv = $("#candidate-buttons");
  const leftPanel = $("#left-panel");

  if (feedbackEl) {
    feedbackEl.textContent = "";
    feedbackEl.className = "";
  }
  if (nextRoundBtn) nextRoundBtn.style.display = "none";
  if (nextLevelBtn) nextLevelBtn.style.display = "none";
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
}

// ==========================
// Interaction handlers
// ==========================

function handleCandidateClick(candidate, round) {
  const pauli = candidate.pauli;
  const stabs = round.stabilizers;

  const safe = isSafeMeasurement(pauli, stabs);

  const feedback = $("#feedback-message");
  const leftPanel = $("#left-panel");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");

  if (safe) {
    if (feedback) {
      feedback.textContent = `✅ Safe: ${candidate.label} anticommutes with at least one stabilizer generator, so it only updates the stabilizer and leaves the logical info intact.`;
      feedback.className = "feedback-safe";
    }
  } else {
    if (feedback) {
      feedback.textContent = `❌ Unsafe: ${candidate.label} commutes with all stabilizers here (in this toy level), so we treat it as measuring a logical operator. Your encoded state would be damaged.`;
      feedback.className = "feedback-unsafe";
    }
    if (leftPanel) {
      leftPanel.classList.remove("shake");
      void leftPanel.offsetWidth; // force reflow so animation can restart
      leftPanel.classList.add("shake");
    }
  }

  if (!hasAnsweredThisRound) {
    hasAnsweredThisRound = true;
    const isLastRound = currentRoundIndex === currentLevel.rounds.length - 1;
    if (isLastRound) {
      if (nextLevelBtn) nextLevelBtn.style.display = "inline-block";
    } else {
      if (nextRoundBtn) nextRoundBtn.style.display = "inline-block";
    }
  }
}

function goToNextRound() {
  if (!currentLevel) return;
  if (currentRoundIndex < currentLevel.rounds.length - 1) {
    currentRoundIndex += 1;
    renderRound();
  }
}

// ==========================
// Initialization
// ==========================

window.addEventListener("DOMContentLoaded", () => {
  console.log("DOM fully loaded, wiring up handlers…");

  const startBtn = $("#start-btn");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");
  const introScreen = $("#intro-screen");
  const gameContainer = $("#game-container");

  if (!startBtn) {
    console.error("start-btn not found in DOM");
    return;
  }

  startBtn.addEventListener("click", async () => {
    console.log("Start button clicked");
    if (introScreen) introScreen.classList.add("hidden");
    if (gameContainer) gameContainer.classList.remove("hidden");

    try {
      const level = await loadLevel("level-1");
      renderLevel(level);
    } catch (err) {
      console.error("Error loading level:", err);
      const levelTitleEl = $("#game-level");
      const levelDescEl = $("#level-description");
      if (levelTitleEl) levelTitleEl.textContent = "Error loading level";
      if (levelDescEl) levelDescEl.textContent = String(err);
    }
  });

  if (nextRoundBtn) {
    nextRoundBtn.addEventListener("click", () => {
      goToNextRound();
    });
  }

  if (nextLevelBtn) {
    nextLevelBtn.addEventListener("click", () => {
      alert("Level 2 will add Bob's entangling unitaries and extractability. (Coming soon!)");
    });
  }
});
