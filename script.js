import {
  catastrophePrompts,
  bunkerDetails,
  archetypeSeeds,
  aiPhrases
} from "./data.js";

const TOTAL_PLAYERS = 8;

const randomChoice = (array) => array[Math.floor(Math.random() * array.length)];

const cryptoRandom = (max) => {
  if (window.crypto && window.crypto.getRandomValues) {
    const buffer = new Uint32Array(1);
    window.crypto.getRandomValues(buffer);
    return buffer[0] % max;
  }
  return Math.floor(Math.random() * max);
};

const aiShuffleSentence = (fragments) => {
  const parts = [...fragments].sort(() => Math.random() - 0.5);
  return parts.join(", ").replace(/, ([^,]*)$/, " і $1");
};

class AIOracle {
  constructor(seeds) {
    this.seeds = seeds;
  }

  generateProfile() {
    const profile = Object.fromEntries(
      Object.entries(this.seeds).map(([key, seed]) => [
        key,
        Array.isArray(seed) ? seed[cryptoRandom(seed.length)] : ""
      ])
    );
    profile.synthetic = this.composeStory(profile);
    profile.age = 18 + cryptoRandom(32);
    profile.callSign = this.createCallSign(profile);
    return profile;
  }

  createCallSign(profile) {
    const adjective = randomChoice([
      "Кристал",
      "Геліос",
      "Азимут",
      "Вектор",
      "Фрактал",
      "Норд",
      "Графіт",
      "Комета"
    ]);
    const noun = profile.profession.split(" ")[0];
    return `${adjective}-${noun.toUpperCase()}`;
  }

  composeStory(profile) {
    const opening = randomChoice(aiPhrases.openings);
    const connector = randomChoice(aiPhrases.connectors);
    const ending = randomChoice(aiPhrases.endings);
    const detail = aiShuffleSentence([
      profile.skill,
      profile.personality,
      profile.baggage,
      profile.twist
    ]);
    return `${opening}: ${detail}, де ${connector}, ${ending}`;
  }
}

class GameState {
  constructor() {
    this.players = [];
    this.scenario = null;
    this.bunker = null;
    this.phaseIndex = 0;
    this.orbitalAI = new AIOracle(archetypeSeeds);
  }

  initialize() {
    this.generateScenario();
    this.generatePlayers();
    this.phaseIndex = 0;
  }

  generateScenario() {
    this.scenario = randomChoice(catastrophePrompts);
    this.bunker = randomChoice(bunkerDetails);
  }

  generatePlayers() {
    this.players = Array.from({ length: TOTAL_PLAYERS }, (_, idx) => ({
      id: idx,
      name: `Гравець ${idx + 1}`,
      eliminated: false,
      profile: this.orbitalAI.generateProfile(),
      trust: 50 + cryptoRandom(40) - 20
    }));
  }

  rerollPlayer(id) {
    const target = this.players.find((player) => player.id === id);
    if (!target) return;
    target.profile = this.orbitalAI.generateProfile();
  }

  togglePlayer(id) {
    const target = this.players.find((player) => player.id === id);
    if (!target) return;
    target.eliminated = !target.eliminated;
  }

  advancePhase() {
    this.phaseIndex = (this.phaseIndex + 1) % phases.length;
  }
}

const phases = ["Ознайомлення", "Дискусія", "Голосування"];

const state = new GameState();

const ui = {
  headerScenario: document.querySelector(".scenario"),
  bunker: document.querySelector(".bunker"),
  flavorList: document.querySelector(".scenario-flavor"),
  playersGrid: document.querySelector(".players-grid"),
  phaseLabel: document.querySelector(".phase-label"),
  trustSummary: document.querySelector(".trust-summary"),
  controls: {
    rerollAll: document.querySelector("#reroll-all"),
    newScenario: document.querySelector("#new-scenario"),
    nextPhase: document.querySelector("#next-phase")
  }
};

const renderScenario = () => {
  const { scenario, bunker } = state;
  if (!scenario || !bunker) return;
  ui.headerScenario.querySelector("h2").textContent = scenario.title;
  ui.headerScenario.querySelector("p").textContent = scenario.summary;
  ui.bunker.innerHTML = `
    <div class="bunker-detail">
      <span>Площа</span>
      <strong>${bunker.size}</strong>
    </div>
    <div class="bunker-detail">
      <span>Запаси</span>
      <strong>${bunker.supplies}</strong>
    </div>
    <div class="bunker-detail">
      <span>Спеціальна перевага</span>
      <strong>${bunker.special}</strong>
    </div>
  `;
  ui.flavorList.innerHTML = scenario.flavor
    .map((note) => `<li>${note}</li>`)
    .join("");
};

const playerTemplate = (player) => {
  const { profile } = player;
  const classes = ["player-card"];
  if (player.eliminated) classes.push("player-card--eliminated");
  return `
    <article class="${classes.join(" ")}" data-player-id="${player.id}">
      <header>
        <div class="avatar">${player.id + 1}</div>
        <div>
          <h3>${player.name}</h3>
          <span class="callsign">${profile.callSign}, ${profile.age}</span>
        </div>
        <button class="icon-button reroll" title="Перегенерувати">⟳</button>
      </header>
      <section class="traits">
        <div><span>Професія</span><p>${profile.profession}</p></div>
        <div><span>Скіл</span><p>${profile.skill}</p></div>
        <div><span>Риси</span><p>${profile.personality}</p></div>
        <div><span>Здоров'я</span><p>${profile.health}</p></div>
        <div><span>Хобі</span><p>${profile.hobby}</p></div>
        <div><span>Багаж</span><p>${profile.baggage}</p></div>
        <div><span>Страх</span><p>${profile.fear}</p></div>
        <div><span>Твіст</span><p>${profile.twist}</p></div>
      </section>
      <footer>
        <p class="ai-story">${profile.synthetic}</p>
        <div class="card-actions">
          <button class="pill-button toggle" data-action="toggle">
            ${player.eliminated ? "Повернути до гри" : "Залишити зовні"}
          </button>
          <div class="trust-meter" title="Рівень довіри">
            <span style="width: ${player.trust}%"></span>
          </div>
        </div>
      </footer>
    </article>
  `;
};

const renderPlayers = () => {
  ui.playersGrid.innerHTML = state.players.map(playerTemplate).join("");
  ui.trustSummary.textContent = calculateTrustMood();
};

const calculateTrustMood = () => {
  const activePlayers = state.players.filter((p) => !p.eliminated);
  if (!activePlayers.length) return "Команда розпалась. Потрібна нова генерація.";
  const avg =
    activePlayers.reduce((sum, player) => sum + player.trust, 0) /
    activePlayers.length;
  if (avg > 70) return "Колектив заряджений взаємною довірою.";
  if (avg > 50) return "Команда напружена, але налаштована конструктивно.";
  if (avg > 30) return "Дискусії стають гострими, довіра тане.";
  return "Група майже розколота. Перегляньте склади.";
};

const renderPhase = () => {
  ui.phaseLabel.textContent = phases[state.phaseIndex];
};

const handleGridClick = (event) => {
  const article = event.target.closest("article");
  if (!article) return;
  const playerId = Number(article.dataset.playerId);
  if (event.target.classList.contains("reroll")) {
    state.rerollPlayer(playerId);
    renderPlayers();
    return;
  }
  if (event.target.dataset.action === "toggle") {
    state.togglePlayer(playerId);
    renderPlayers();
  }
};

const handleRerollAll = () => {
  state.generatePlayers();
  renderPlayers();
};

const handleNewScenario = () => {
  state.generateScenario();
  renderScenario();
};

const handleNextPhase = () => {
  state.advancePhase();
  renderPhase();
};

const initializeApp = () => {
  state.initialize();
  renderScenario();
  renderPlayers();
  renderPhase();
  ui.playersGrid.addEventListener("click", handleGridClick);
  ui.controls.rerollAll.addEventListener("click", handleRerollAll);
  ui.controls.newScenario.addEventListener("click", handleNewScenario);
  ui.controls.nextPhase.addEventListener("click", handleNextPhase);
};

document.addEventListener("DOMContentLoaded", initializeApp);
