// ===== Utility: Pauli commutation =====

// Given two single-qubit Paulis a,b in {I,X,Y,Z}, do they anticommute?
function singleAnticommute(a, b) {
  if (a === 'I' || b === 'I' || a === b) {
    return false;
  }
  // X,Y,Z anticommute whenever they are different non-I Paulis
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

// ===== DOM helpers =====

function $(selector) {
  return document.querySelector(selector);
}

// ===== Game state =====

let currentLevel = null;
let currentRoundIndex = 0;
let hasAnsweredThisRound = false;

// ===== Level loading and rendering =====

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
  $("#game-level").textContent = level.title;
  $("#level-description").textContent = level.description;
  $("#round-progress").textContent = `Round ${currentRoundIndex + 1} of ${level.rounds.length}`;
  renderRound();
}

function renderRound() {
  const level = currentLevel;
  const round = level.rounds[currentRoundIndex];

  hasAnsweredThisRound = false;
  $("#feedback-message").textContent = "";
  $("#feedback-message").className = "";
  $("#next-round-btn").style.display = "none";
  $("#next-level-btn").style.display = "none";

  // Round labels/text
  $("#round-label").textContent = round.label || `Round ${currentRoundIndex + 1}`;
  $("#round-text").textContent = round.text || "";

  // Update progress
  $("#round-progress").textContent = `Round ${currentRoundIndex + 1} of ${level.rounds.length}`;

  // Graph image
  const graphImg = $("#graph-image");
  if (round.graphImage) {
    graphImg.src = round.graphImage;
    graphImg.style.display = "block";
  } else {
    graphImg.style.display = "none";
  }

  // Circuit image
  const circImg = $("#circuit-image");
  if (round.circuitImage) {
    circImg.src = round.circuitImage;
    circImg.style.display = "block";
  } else {
    circImg.style.display = "none";
  }

  // Stabilizers
  const stabilizerList = $("#stabilizer-list");
  stabilizerList.innerHTML = "";
  round.stabilizers.forEach((S, idx) => {
    const li = document.createElement("li");
    li.textContent = `S${idx + 1} = ${S}`;
    stabilizerList.appendChild(li);
  });

  // Candidate buttons
  const buttonsDiv = $("#candidate-buttons");
  buttonsDiv.innerHTML = "";
  const leftPanel = $("#left-panel");
  leftPanel.classList.remove("shake");

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

// ===== Interaction handlers =====

function handleCandidateClick(candidate, round) {
  const pauli = candidate.pauli;
  const stabs = round.stabilizers;

  const safe = isSafeMeasurement(pauli, stabs);

  const feedback = $("#feedback-message");
  const leftPanel = $("#left-panel");

  if (safe) {
    feedback.textContent = `✅ Safe: ${candidate.label} anticommutes with at least one stabilizer generator, so it only updates the stabilizer and leaves the logical info intact.`;
    feedback.className = "feedback-safe";
  } else {
    feedback.textContent = `❌ Unsafe: ${candidate.label} commutes with all stabilizers here (in this toy level), so we treat it as measuring a logical operator. Your encoded state would be damaged.`;
    feedback.className = "feedback-unsafe";
    leftPanel.classList.remove("shake");
    void leftPanel.offsetWidth; // force reflow so animation can restart
    leftPanel.classList.add("shake");
  }

  // After first answer, show next-round or next-level button.
  if (!hasAnsweredThisRound) {
    hasAnsweredThisRound = true;
    const isLastRound = (currentRoundIndex === currentLevel.rounds.length - 1);
    if (isLastRound) {
      $("#next-level-btn").style.display = "inline-block";
    } else {
      $("#next-round-btn").style.display = "inline-block";
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

// ===== Initialization =====

window.addEventListener("DOMContentLoaded", async () => {
  // Hook up buttons
  const startBtn = $("#start-btn");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");

  if (startBtn) {
    startBtn.addEventListener("click", async () => {
      $("#intro-screen").classList.add("hidden");
      $("#game-container").classList.remove("hidden");
      try {
        const level = await loadLevel("level-1");
        renderLevel(level);
      } catch (err) {
        console.error(err);
        $("#game-level").textContent = "Error loading level";
        $("#level-description").textContent = err.toString();
      }
    });
  }

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
