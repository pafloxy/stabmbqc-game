// ==========================
// Utility: Pauli commutation
// ==========================

function singleAnticommute(a, b) {
  if (a === 'I' || b === 'I' || a === b) {
    return false;
  }
  return true;
}

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
let level1Data = null;
let currentRoundIndex = 0;
let hasAnsweredThisRound = false;

// slides state
let currentSlides = [];
let currentSlideIndex = 0;
let slidesDoneCallback = null;

// timer state
let roundTimerId = null;
let remainingSeconds = 0;
let timerPaused = false;

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
// Info overlay
// ==========================

function showInfoOverlay() {
  const infoOverlay = $("#info-overlay");
  if (!infoOverlay) return;

  // pause timer if running
  if (!hasAnsweredThisRound && remainingSeconds > 0 && roundTimerId !== null) {
    clearRoundTimer();
    timerPaused = true;
  } else {
    timerPaused = false;
  }

  infoOverlay.classList.remove("hidden");
}

function hideInfoOverlay() {
  const infoOverlay = $("#info-overlay");
  if (!infoOverlay) return;

  infoOverlay.classList.add("hidden");

  if (timerPaused && !hasAnsweredThisRound && remainingSeconds > 0) {
    startRoundTimer(remainingSeconds);
  }
  timerPaused = false;
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
      void leftPanel.offsetWidth;
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

function restartGame() {
  clearRoundTimer();
  hasAnsweredThisRound = false;
  currentRoundIndex = 0;
  const gameContainer = $("#game-container");
  if (gameContainer) gameContainer.classList.add("hidden");

  const onSlidesDone = () => {
    if (gameContainer) gameContainer.classList.remove("hidden");
    if (level1Data) {
      renderLevel(level1Data);
    }
  };

  if (level1Data && level1Data.introSlides && level1Data.introSlides.length > 0) {
    showSlides(level1Data.introSlides, onSlidesDone);
  } else {
    hideSlides();
    onSlidesDone();
  }
}

// ==========================
// Initialization
// ==========================

window.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM fully loaded, setting up...");

  const slidesPrevBtn = $("#slide-prev-btn");
  const slidesNextBtn = $("#slide-next-btn");
  const slidesStartBtn = $("#slide-start-level-btn");
  const slidesSkipBtn = $("#slide-skip-btn");
  const nextRoundBtn = $("#next-round-btn");
  const nextLevelBtn = $("#next-level-btn");
  const restartLevelBtn = $("#restart-level-btn");
  const restartGameBtn = $("#restart-game-btn");
  const rulesBtn = $("#rules-btn");
  const infoCloseBtn = $("#info-close-btn");
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
      hideSlides();
      if (slidesDoneCallback) slidesDoneCallback();
    });
  }

  if (slidesSkipBtn) {
    slidesSkipBtn.addEventListener("click", () => {
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

  if (restartLevelBtn) {
    restartLevelBtn.addEventListener("click", () => {
      restartLevel();
    });
  }

  if (restartGameBtn) {
    restartGameBtn.addEventListener("click", () => {
      restartGame();
    });
  }

  if (rulesBtn) {
    rulesBtn.addEventListener("click", () => {
      showInfoOverlay();
    });
  }

  if (infoCloseBtn) {
    infoCloseBtn.addEventListener("click", () => {
      hideInfoOverlay();
    });
  }

  try {
    const level = await loadLevel("level-1");
    level1Data = level;

    const onSlidesDone = () => {
      if (gameContainer) gameContainer.classList.remove("hidden");
      renderLevel(level1Data);
    };

    if (level1Data.introSlides && level1Data.introSlides.length > 0) {
      showSlides(level1Data.introSlides, onSlidesDone);
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
