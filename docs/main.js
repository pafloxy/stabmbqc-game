// ==========================
// StabMBQC Game - Main JS
// State machine + rendering
// ==========================

// ==========================
// Global State
// ==========================

const appState = {
  phase: "home", // home | intro | info | round | gameover | victory
  previousPhase: null, // for returning from info overlay
  introIndex: 0,
  roundIndex: 0,
  stepIndex: 0,
  selectedOptionId: null,
  hasAnsweredThisStep: false,
  timer: { active: false, remaining: 0, handle: null },
  stats: { correct: 0, wrong: 0 }
};

let campaignData = null;
const slideTextCache = new Map();
const roundContextCache = new Map();
const stepPromptCache = new Map();
const infoOverlayState = { mode: "rules" };

// ==========================
// DOM helpers
// ==========================

function $(selector) {
  return document.querySelector(selector);
}

function $$(selector) {
  return document.querySelectorAll(selector);
}

function markdownToHtml(text) {
  return (text || "").replace(/\n/g, "<br>");
}

// ==========================
// LaTeX rendering with MathJax
// ==========================

function renderLatex(element = document.body) {
  // Re-render MathJax for dynamically added content
  if (window.MathJax && window.MathJax.typesetPromise) {
    window.MathJax.typesetPromise([element]).catch((err) => {
      console.warn("MathJax rendering error:", err.message);
    });
  }
}

// ==========================
// Typewriter effect
// ==========================

const typewriterState = new WeakMap();

function stopTypewriter(el) {
  const state = typewriterState.get(el);
  if (state?.handle) {
    clearTimeout(state.handle);
  }
  el?.classList?.remove("is-typing");
  typewriterState.delete(el);
}

function typeTextIntoElement(el, text = "", options = {}) {
  if (!el) return;

  const chunkSize = options.chunkSize || 3;
  const delayMs = options.delayMs || 2;

  stopTypewriter(el);
  const token = Symbol("typewriter");
  const state = { token, handle: null };
  typewriterState.set(el, state);

  el.textContent = "";
  el.classList.add("typewriter", "is-typing");

  let index = 0;
  const revealNext = () => {
    if (typewriterState.get(el)?.token !== token) return;

    el.textContent = text.slice(0, index);
    index += chunkSize;

    if (index <= text.length) {
      state.handle = setTimeout(revealNext, delayMs);
    } else {
      stopTypewriter(el);
      el.textContent = text;
      if (typeof options.onComplete === "function") {
        options.onComplete();
      }
    }
  };

  revealNext();
}

// ==========================
// Intro slide text loader (supports textPath)
// ==========================

async function getSlideText(slide) {
  if (!slide) return "";
  if (slide.body_markdown) return slide.body_markdown;
  if (slide.text) return slide.text;
  if (!slide.textPath) return "";

  if (slideTextCache.has(slide.textPath)) {
    return slideTextCache.get(slide.textPath);
  }

  try {
    const resp = await fetch(slide.textPath);
    if (!resp.ok) {
      throw new Error(`Failed to load slide text from ${slide.textPath}`);
    }
    const txt = await resp.text();
    slideTextCache.set(slide.textPath, txt);
    return txt;
  } catch (err) {
    console.warn(err.message);
    return "";
  }
}

function setSlideBodyText(slide, el) {
  if (!el || !slide) return;
  const cacheKey = slide.id || `slide-${Date.now()}`;
  el.dataset.slideId = cacheKey;
  el.textContent = "Loading...";
  el.classList.add("typewriter");

  getSlideText(slide).then((text) => {
    // Avoid race: only update if still same slide element
    if (el.dataset.slideId === cacheKey) {
      typeTextIntoElement(el, text, {
        delayMs: 12,
        chunkSize: 1,
        onComplete: () => {
          if (el.dataset.slideId === cacheKey) {
            renderLatex(el);
          }
        }
      });
    }
  });
}

// ==========================
// Round context text loader (supports contextPath)
// ==========================

async function getRoundContext(round) {
  if (!round) return "";
  if (round.context_markdown) return round.context_markdown;
  if (!round.contextPath) return "";

  if (roundContextCache.has(round.contextPath)) {
    return roundContextCache.get(round.contextPath);
  }

  try {
    const resp = await fetch(round.contextPath);
    if (!resp.ok) {
      throw new Error(`Failed to load round context from ${round.contextPath}`);
    }
    const txt = await resp.text();
    roundContextCache.set(round.contextPath, txt);
    return txt;
  } catch (err) {
    console.warn(err.message);
    return "";
  }
}

// ==========================
// Step prompt text loader (supports promptPath)
// ==========================

async function getStepPrompt(step) {
  if (!step) return "Make your choice:";
  if (step.prompt_markdown) return step.prompt_markdown;
  if (!step.promptPath) return "Make your choice:";

  if (stepPromptCache.has(step.promptPath)) {
    return stepPromptCache.get(step.promptPath);
  }

  try {
    const resp = await fetch(step.promptPath);
    if (!resp.ok) {
      throw new Error(`Failed to load step prompt from ${step.promptPath}`);
    }
    const txt = await resp.text();
    stepPromptCache.set(step.promptPath, txt);
    return txt;
  } catch (err) {
    console.warn(err.message);
    return "Make your choice:";
  }
}

// ==========================
// Asset path resolver
// ==========================

function resolveAssetPath(relativePath) {
  if (!campaignData || !relativePath) return relativePath;
  const base = campaignData.meta?.assets_base || "assets";
  return `${base}/${relativePath}`;
}

// ==========================
// Timer logic
// ==========================

function startTimer(seconds, onExpire) {
  stopTimer();
  if (!seconds || seconds <= 0) return;
  
  appState.timer.active = true;
  appState.timer.remaining = seconds;
  updateTimerUI(seconds);

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
  if (appState.timer.handle) {
    clearInterval(appState.timer.handle);
  }
  appState.timer.handle = null;
  appState.timer.active = false;
}

function updateTimerUI(seconds) {
  const timerEl = $("#timer-value");
  if (timerEl) {
    timerEl.textContent = seconds > 0 ? seconds.toString() : "--";
  }
}

// ==========================
// Cheat code handling
// ==========================

function tryCheatCode() {
  if (!campaignData?.config?.cheat?.enabled) {
    alert("Cheat codes are disabled.");
    return;
  }
  
  const code = prompt("Enter cheat code:");
  if (code && code.toUpperCase() === campaignData.config.cheat.code.toUpperCase()) {
    advanceToNextRound();
  } else if (code) {
    alert("Invalid cheat code!");
  }
}

// ==========================
// Navigation helpers
// ==========================

function advanceToNextStep() {
  const round = getCurrentRound();
  if (!round) return;

  if (appState.stepIndex < round.steps.length - 1) {
    appState.stepIndex += 1;
    appState.hasAnsweredThisStep = false;
    appState.selectedOptionId = null;
    render();
  } else {
    advanceToNextRound();
  }
}

function advanceToNextRound() {
  stopTimer();
  
  if (appState.roundIndex < campaignData.rounds.length - 1) {
    appState.roundIndex += 1;
    appState.stepIndex = 0;
    appState.hasAnsweredThisStep = false;
    appState.selectedOptionId = null;
    appState.phase = "round";
    render();
  } else {
    appState.phase = "victory";
    render();
  }
}

function getCurrentRound() {
  if (!campaignData?.rounds) return null;
  return campaignData.rounds[appState.roundIndex] || null;
}

function getCurrentStep() {
  const round = getCurrentRound();
  if (!round?.steps) return null;
  return round.steps[appState.stepIndex] || null;
}

function restartGame() {
  stopTimer();
  appState.phase = "home";
  appState.previousPhase = null;
  appState.introIndex = 0;
  appState.roundIndex = 0;
  appState.stepIndex = 0;
  appState.selectedOptionId = null;
  appState.hasAnsweredThisStep = false;
  appState.stats = { correct: 0, wrong: 0 };
  render();
}

function goToHome() {
  stopTimer();
  appState.phase = "home";
  render();
}

// ==========================
// Info / Hints overlay
// ==========================

function hydrateInfoOverlay() {
  const infoData = campaignData?.info || {};
  const rulesBody = $("#info-body-rules");
  const hintsBody = $("#info-body-hints");

  if (rulesBody) {
    rulesBody.innerHTML = markdownToHtml(infoData.markdown || "No rules available yet.");
  }
  if (hintsBody) {
    hintsBody.innerHTML = markdownToHtml(infoData.hints_markdown || "No hints available yet.");
  }
}

function setInfoOverlayMode(mode = "rules") {
  infoOverlayState.mode = mode;
  const rulesSection = $("#info-body-rules");
  const hintsSection = $("#info-body-hints");
  const rulesTab = $("#info-tab-rules");
  const hintsTab = $("#info-tab-hints");

  rulesSection?.classList.toggle("hidden", mode !== "rules");
  hintsSection?.classList.toggle("hidden", mode !== "hints");
  rulesTab?.classList.toggle("active", mode === "rules");
  hintsTab?.classList.toggle("active", mode === "hints");
}

function showInfoOverlay(mode = "rules") {
  hydrateInfoOverlay();
  setInfoOverlayMode(mode);
  const overlay = $("#info-overlay");
  if (overlay) {
    overlay.classList.remove("hidden");
    renderLatex(overlay);
  }
}

function hideInfoOverlay() {
  const overlay = $("#info-overlay");
  if (overlay) {
    overlay.classList.add("hidden");
  }
}

function initInfoOverlayEvents() {
  $("#info-close-btn")?.addEventListener("click", hideInfoOverlay);
  $("#info-tab-rules")?.addEventListener("click", () => showInfoOverlay("rules"));
  $("#info-tab-hints")?.addEventListener("click", () => showInfoOverlay("hints"));
  $("#info-overlay")?.addEventListener("click", (evt) => {
    if (evt.target.id === "info-overlay") {
      hideInfoOverlay();
    }
  });
}

// ==========================
// Main render dispatcher
// ==========================

function render() {
  const app = $("#app");
  if (!app) return;

  switch (appState.phase) {
    case "home":
      renderHome(app);
      break;
    case "intro":
      renderIntro(app);
      break;
    case "info":
      showInfoOverlay(infoOverlayState.mode || "rules");
      renderHome(app);
      break;
    case "round":
      renderRound(app);
      break;
    case "gameover":
      renderGameOver(app);
      break;
    case "victory":
      renderVictory(app);
      break;
    default:
      renderHome(app);
  }
  
  // Render LaTeX after DOM update
  renderLatex(app);
}

// ==========================
// Render: Home
// ==========================

function renderHome(container) {
  const title = campaignData?.meta?.title || "Measurement Survival";
  const subtitle = campaignData?.meta?.subtitle || "";

  container.innerHTML = `
    <div class="screen home-screen">
      <div class="home-content">
        <h1 class="game-title">${title}</h1>
        ${subtitle ? `<p class="game-subtitle">${subtitle}</p>` : ""}
        <div class="home-buttons">
          <button id="start-btn" class="primary-btn">START</button>
          <button id="info-btn" class="secondary-btn">INFO</button>
        </div>
        <p class="home-footer">Press START to begin your mission</p>
      </div>
    </div>
  `;

  $("#start-btn")?.addEventListener("click", () => {
    if (campaignData?.intro_slides?.length > 0) {
      appState.phase = "intro";
      appState.introIndex = 0;
    } else {
      appState.phase = "round";
      appState.roundIndex = 0;
      appState.stepIndex = 0;
    }
    render();
  });

  $("#info-btn")?.addEventListener("click", () => {
    showInfoOverlay("rules");
  });
}

// ==========================
// Render: Intro
// ==========================

function renderIntro(container) {
  const slides = campaignData?.intro_slides || [];
  const slide = slides[appState.introIndex];
  
  if (!slide) {
    appState.phase = "round";
    appState.roundIndex = 0;
    appState.stepIndex = 0;
    render();
    return;
  }

  const atFirst = appState.introIndex === 0;
  const atLast = appState.introIndex === slides.length - 1;

  let imagesHtml = "";
  if (slide.images && slide.images.length > 0) {
    imagesHtml = `<div class="slide-images">
      ${slide.images.map(img => `<img src="${resolveAssetPath(img)}" alt="Slide image" />`).join("")}
    </div>`;
  }

  container.innerHTML = `
    <div class="screen intro-screen">
      <div class="intro-content">
        <h1 class="slide-title">${slide.title || ""}</h1>
        <div class="slide-body"></div>
        ${imagesHtml}
        <div class="intro-controls">
          <div class="intro-left">
            <button id="prev-btn" class="secondary-btn" ${atFirst ? "disabled" : ""}>◀ BACK</button>
            <button id="next-btn" class="secondary-btn" ${atLast ? 'style="display:none"' : ""}>NEXT ▶</button>
            <button id="start-level-btn" class="primary-btn" ${!atLast ? 'style="display:none"' : ""}>START LEVEL</button>
          </div>
          <div class="intro-right">
            <button id="skip-btn" class="secondary-btn">SKIP INTRO</button>
          </div>
        </div>
      </div>
    </div>
  `;

  $("#prev-btn")?.addEventListener("click", () => {
    if (appState.introIndex > 0) {
      appState.introIndex -= 1;
      render();
    }
  });

  $("#next-btn")?.addEventListener("click", () => {
    if (appState.introIndex < slides.length - 1) {
      appState.introIndex += 1;
      render();
    }
  });

  $("#start-level-btn")?.addEventListener("click", () => {
    appState.phase = "round";
    appState.roundIndex = 0;
    appState.stepIndex = 0;
    render();
  });

  $("#skip-btn")?.addEventListener("click", () => {
    appState.phase = "round";
    appState.roundIndex = 0;
    appState.stepIndex = 0;
    render();
  });

  const slideBody = container.querySelector(".slide-body");
  setSlideBodyText(slide, slideBody);
}

// ==========================
// Render: Info
// ==========================

function renderInfo(container) {
  const infoData = campaignData?.info || {};
  const markdown = infoData.markdown || "# Rulebook\n\nNo rules available.";

  container.innerHTML = `
    <div class="screen info-screen">
      <div class="info-content">
        <div class="info-text">${markdown.replace(/\n/g, "<br>")}</div>
        <div class="info-controls">
          <button id="info-close-btn" class="primary-btn">BACK TO GAME</button>
        </div>
      </div>
    </div>
  `;

  $("#info-close-btn")?.addEventListener("click", () => {
    appState.phase = appState.previousPhase || "home";
    appState.previousPhase = null;
    render();
  });
}

// ==========================
// Render: Round
// ==========================

function renderRound(container) {
  const round = getCurrentRound();
  const step = getCurrentStep();

  if (!round || !step) {
    appState.phase = "victory";
    render();
    return;
  }

  const totalRounds = campaignData.rounds.length;
  const totalSteps = round.steps.length;

  // Build assets HTML
  let assetsHtml = "";
  if (round.assets?.circuit_image || round.assets?.graph_image) {
    assetsHtml = `<div class="round-assets">
      ${round.assets.graph_image ? `<img src="${resolveAssetPath(round.assets.graph_image)}" alt="Graph" class="asset-img" onerror="this.style.display='none'" />` : ""}
      ${round.assets.circuit_image ? `<img src="${resolveAssetPath(round.assets.circuit_image)}" alt="Circuit" class="asset-img" onerror="this.style.display='none'" />` : ""}
    </div>`;
  }

  // Build options HTML
  const optionsHtml = step.options.map(opt => `
    <button class="option-btn ${appState.selectedOptionId === opt.id ? 'selected' : ''}" 
            data-id="${opt.id}" 
            ${appState.hasAnsweredThisStep ? 'disabled' : ''}>
      <span class="option-id">${opt.id}</span>
      <span class="option-label">${opt.label}</span>
    </button>
  `).join("");

  // Feedback HTML
  let feedbackHtml = "";
  if (appState.hasAnsweredThisStep && appState.selectedOptionId) {
    const isCorrect = appState.selectedOptionId === step.answer.correct_option_id;
    const fbText = isCorrect 
      ? (step.feedback?.on_correct_markdown || "Correct!") 
      : (step.feedback?.on_wrong_markdown || "Wrong!");
    feedbackHtml = `<div class="feedback ${isCorrect ? 'feedback-correct' : 'feedback-wrong'}">${fbText}</div>`;
  }

  // Next button logic
  let controlsHtml = "";
  if (appState.hasAnsweredThisStep) {
    const isCorrect = appState.selectedOptionId === step.answer.correct_option_id;
    if (isCorrect) {
      const isLastStep = appState.stepIndex === totalSteps - 1;
      const isLastRound = appState.roundIndex === totalRounds - 1;
      
      if (isLastStep && isLastRound) {
        controlsHtml = `<button id="victory-btn" class="primary-btn">VICTORY!</button>`;
      } else if (isLastStep) {
        controlsHtml = `<button id="next-round-btn" class="primary-btn">NEXT ROUND ▶</button>`;
      } else {
        controlsHtml = `<button id="next-step-btn" class="primary-btn">NEXT STEP ▶</button>`;
      }
    }
  }

  container.innerHTML = `
    <div class="screen round-screen">
      <header class="round-header">
        <div class="header-left">
          <h1 class="round-title">${round.title}</h1>
          <div class="round-progress">Round ${appState.roundIndex + 1}/${totalRounds} • Step ${appState.stepIndex + 1}/${totalSteps}</div>
        </div>
        <div class="header-right">
          <div class="timer-box">TIME: <span id="timer-value">--</span>s</div>
          <div class="header-buttons">
            <button id="rules-btn" class="secondary-btn small">RULES</button>
            <button id="hints-btn" class="secondary-btn small">HINTS</button>
            <button id="skip-round-btn" class="secondary-btn small">SKIP</button>
            <button id="restart-game-btn" class="secondary-btn small">RESTART</button>
          </div>
        </div>
      </header>

      <main class="round-main">
        <div class="round-left">
          ${assetsHtml}
          <div class="context-box" id="round-context-box">
            <p>Loading context...</p>
          </div>
        </div>
        
        <div class="round-right">
          <div class="step-prompt" id="step-prompt-box">
            <h2>Loading prompt...</h2>
          </div>
          
          <div class="options-container">
            ${optionsHtml}
          </div>

          <div class="feedback-box">
            ${feedbackHtml}
          </div>

          <div class="round-controls">
            ${controlsHtml}
          </div>
        </div>
      </main>
    </div>
  `;
  // Load and render round context
  const contextBox = $("#round-context-box");
  if (contextBox) {
    getRoundContext(round).then((text) => {
      contextBox.innerHTML = `<p>${markdownToHtml(text)}</p>`;
      renderLatex(contextBox);
    });
  }

  // Load and render step prompt
  const promptBox = $("#step-prompt-box");
  if (promptBox) {
    getStepPrompt(step).then((text) => {
      promptBox.innerHTML = `<h2>${markdownToHtml(text)}</h2>`;
      renderLatex(promptBox);
    });
  }

  // Wire up event handlers
  $$(".option-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (appState.hasAnsweredThisStep) return;
      handleOptionClick(btn.dataset.id);
    });
  });

  $("#rules-btn")?.addEventListener("click", () => {
    showInfoOverlay("rules");
  });

  $("#hints-btn")?.addEventListener("click", () => {
    showInfoOverlay("hints");
  });

  $("#skip-round-btn")?.addEventListener("click", () => {
    tryCheatCode();
  });

  $("#restart-game-btn")?.addEventListener("click", () => {
    restartGame();
  });

  $("#next-step-btn")?.addEventListener("click", () => {
    advanceToNextStep();
  });

  $("#next-round-btn")?.addEventListener("click", () => {
    advanceToNextRound();
  });

  $("#victory-btn")?.addEventListener("click", () => {
    appState.phase = "victory";
    render();
  });

  // Start timer if not answered
  if (!appState.hasAnsweredThisStep) {
    const timerConfig = step.timer || campaignData.config?.timer;
    if (timerConfig?.enabled) {
      const seconds = step.timer?.seconds || campaignData.config?.timer?.seconds_per_step || 300;
      startTimer(seconds, () => {
        appState.phase = "gameover";
        render();
      });
    }
  }
}

function handleOptionClick(optionId) {
  if (appState.hasAnsweredThisStep) return;
  
  stopTimer();
  appState.selectedOptionId = optionId;
  appState.hasAnsweredThisStep = true;

  const step = getCurrentStep();
  const isCorrect = optionId === step.answer.correct_option_id;

  if (isCorrect) {
    appState.stats.correct += 1;
  } else {
    appState.stats.wrong += 1;
  }

  render();
}

// ==========================
// Render: Game Over
// ==========================

function renderGameOver(container) {
  container.innerHTML = `
    <div class="screen gameover-screen">
      <div class="gameover-content">
        <h1 class="gameover-title">GAME OVER</h1>
        <p class="gameover-message">The measurement hacker got through!</p>
        <div class="gameover-stats">
          <p>Correct answers: ${appState.stats.correct}</p>
          <p>Rounds completed: ${appState.roundIndex}</p>
        </div>
        <div class="gameover-buttons">
          <button id="restart-btn" class="primary-btn">RESTART GAME</button>
          <button id="home-btn" class="secondary-btn">BACK TO HOME</button>
        </div>
      </div>
    </div>
  `;

  $("#restart-btn")?.addEventListener("click", () => {
    restartGame();
  });

  $("#home-btn")?.addEventListener("click", () => {
    goToHome();
  });
}

// ==========================
// Render: Victory
// ==========================

function renderVictory(container) {
  container.innerHTML = `
    <div class="screen victory-screen">
      <div class="victory-content">
        <h1 class="victory-title">VICTORY!</h1>
        <p class="victory-message">You protected the logical qubit!</p>
        <div class="victory-stats">
          <p>Total correct: ${appState.stats.correct}</p>
          <p>Rounds completed: ${campaignData?.rounds?.length || 0}</p>
        </div>
        <div class="victory-buttons">
          <button id="restart-btn" class="primary-btn">PLAY AGAIN</button>
          <button id="home-btn" class="secondary-btn">BACK TO HOME</button>
        </div>
      </div>
    </div>
  `;

  $("#restart-btn")?.addEventListener("click", () => {
    restartGame();
  });

  $("#home-btn")?.addEventListener("click", () => {
    goToHome();
  });
}

// ==========================
// Level loading
// ==========================

async function loadLevel(levelId) {
  const response = await fetch(`levels/${levelId}.json`);
  if (!response.ok) {
    throw new Error(`Could not load level file for ${levelId}`);
  }
  return await response.json();
}

// ==========================
// Initialization
// ==========================

window.addEventListener("DOMContentLoaded", async () => {
  console.log("StabMBQC Game initializing...");
  initInfoOverlayEvents();

  try {
    campaignData = await loadLevel("level-1");
    console.log("Campaign data loaded:", campaignData);
    hydrateInfoOverlay();
    
    appState.phase = "home";
    render();
  } catch (err) {
    console.error("Error loading level:", err);
    const app = $("#app");
    if (app) {
      app.innerHTML = `
        <div class="screen error-screen">
          <h1>Error Loading Game</h1>
          <p>${err.message}</p>
        </div>
      `;
    }
  }
});
