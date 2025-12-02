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

// ===== Game logic =====

async function loadLevel(levelId) {
  const response = await fetch(`levels/${levelId}.json`);
  if (!response.ok) {
    throw new Error(`Could not load level file for ${levelId}`);
  }
  const levelData = await response.json();
  return levelData;
}

function renderLevel(level) {
  // Set title and level text
  $("#game-level").textContent = level.title;
  $("#level-description").textContent = level.description;

  // Set graph image if provided
  const graphImg = $("#graph-image");
  if (level.graphImage) {
    graphImg.src = level.graphImage;
    graphImg.style.display = "block";
  } else {
    graphImg.style.display = "none";
  }

  // Render stabilizers
  const stabilizerList = $("#stabilizer-list");
  stabilizerList.innerHTML = "";
  level.stabilizers.forEach((S, idx) => {
    const li = document.createElement("li");
    li.textContent = `S${idx + 1} = ${S}`;
    stabilizerList.appendChild(li);
  });

  // Render candidate buttons
  const buttonsDiv = $("#candidate-buttons");
  buttonsDiv.innerHTML = "";
  $("#feedback-message").textContent = "";
  $("#feedback-message").className = "";
  const leftPanel = $("#left-panel");
  leftPanel.classList.remove("shake");

  level.candidates.forEach((cand) => {
    const btn = document.createElement("button");
    btn.className = "candidate-btn";
    btn.textContent = cand.label;
    btn.addEventListener("click", () => {
      handleCandidateClick(cand, level);
    });
    buttonsDiv.appendChild(btn);
  });
}

// Handle a click on a candidate measurement
function handleCandidateClick(candidate, level) {
  const pauli = candidate.pauli;
  const stabs = level.stabilizers;

  const safe = isSafeMeasurement(pauli, stabs);

  const feedback = $("#feedback-message");
  const leftPanel = $("#left-panel");

  if (safe) {
    feedback.textContent = `✅ Safe: ${candidate.label} anticommutes with at least one stabilizer generator, so it only updates the stabilizer and leaves the logical info intact.`;
    feedback.className = "feedback-safe";
  } else {
    feedback.textContent = `❌ Unsafe: ${candidate.label} commutes with all stabilizers here, so in this toy level we treat it as measuring a logical operator. Your encoded state would be damaged.`;
    feedback.className = "feedback-unsafe";
    // shake the left panel for dramatic effect
    leftPanel.classList.remove("shake");
    void leftPanel.offsetWidth; // force reflow so animation can restart
    leftPanel.classList.add("shake");
  }
}

// ===== Initialization =====

window.addEventListener("DOMContentLoaded", async () => {
  try {
    const level = await loadLevel("level-1");
    renderLevel(level);
  } catch (err) {
    console.error(err);
    $("#game-level").textContent = "Error loading level";
    $("#level-description").textContent = err.toString();
  }
});
