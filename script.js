const ui = {
  status: document.querySelector('[data-connection-status]'),
  sections: document.querySelectorAll('[data-section]'),
  createRoom: document.getElementById('create-room'),
  joinForm: document.getElementById('join-form'),
  lobbyRoomInfo: document.querySelector('[data-room-info]'),
  lobbyRoomCode: document.querySelector('[data-room-code]'),
  lobbyRevealProgress: document.querySelector('[data-reveal-progress]'),
  lobbyRevealTotal: document.querySelector('[data-reveal-total]'),
  host: {
    panel: document.querySelector('[data-section="host"]'),
    code: document.querySelector('[data-host-code]'),
    scenarioTitle: document.querySelector('[data-scenario-title]'),
    scenarioSummary: document.querySelector('[data-scenario-summary]'),
    scenarioFlavor: document.querySelector('[data-scenario-flavor]'),
    bunkerSize: document.querySelector('[data-bunker-size]'),
    bunkerSupplies: document.querySelector('[data-bunker-supplies]'),
    bunkerSpecial: document.querySelector('[data-bunker-special]'),
    revealTrack: document.querySelector('[data-reveal-track]'),
    revealLabel: document.querySelector('[data-reveal-label]'),
    revealNext: document.getElementById('reveal-next'),
    resetReveal: document.getElementById('reset-reveal'),
    grid: document.querySelector('[data-host-grid]')
  },
  player: {
    panel: document.querySelector('[data-section="player"]'),
    code: document.querySelector('[data-player-code]'),
    name: document.querySelector('[data-player-name]'),
    callSign: document.querySelector('[data-player-callsign]'),
    age: document.querySelector('[data-player-age]'),
    traits: document.querySelector('[data-player-traits]'),
    video: document.querySelector('[data-player-video]'),
    overlay: document.querySelector('[data-video-overlay]')
  },
  toast: document.querySelector('[data-toast]'),
  hostCardTemplate: document.getElementById('host-player-card')
};

const traitLabels = {
  profession: 'Професія',
  skill: 'Навичка',
  personality: 'Характер',
  health: "Здоров'я",
  hobby: 'Хобі',
  baggage: 'Багаж',
  fear: 'Страх',
  twist: 'Твіст',
  synthetic: 'Наратив ШІ'
};

const state = {
  role: 'guest',
  traitSequence: [],
  revealStage: 0,
  scenario: null,
  bunker: null,
  host: {
    code: null,
    token: null,
    events: null
  },
  player: {
    code: null,
    token: null,
    slot: null,
    profile: null,
    name: null,
    events: null
  }
};

const setConnectionStatus = (online) => {
  ui.status.dataset.online = online ? 'true' : 'false';
  ui.status.textContent = online ? 'online' : 'offline';
};

let activeEventStreams = 0;

const trackConnection = (online) => {
  activeEventStreams = Math.max(0, online ? activeEventStreams + 1 : activeEventStreams - 1);
  setConnectionStatus(activeEventStreams > 0);
};

const showSection = (target) => {
  ui.sections.forEach((section) => {
    section.classList.toggle('hidden', section.dataset.section !== target);
  });
};

const showToast = (message, timeout = 3200) => {
  if (!ui.toast) return;
  ui.toast.textContent = message;
  ui.toast.classList.remove('hidden');
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => {
    ui.toast.classList.add('hidden');
  }, timeout);
};

const uppercaseCode = (value) => (value || '').toString().trim().toUpperCase();

const buildTraitList = (profile, revealStage, traitSequence, options = {}) => {
  if (!profile || !traitSequence.length) return '';
  const unlocked = Math.min(revealStage, traitSequence.length);
  return traitSequence
    .map((key, index) => {
      const label = traitLabels[key] || key;
      const value = profile[key] || '—';
      const revealed = index < unlocked;
      const classes = ['trait', revealed ? 'revealed' : 'locked'];
      const labelMarkup = options.compact
        ? `<strong class="trait-title">${label}</strong>`
        : `<span class="trait-title">${label}</span>`;
      const displayValue = revealed || options.revealAll ? value : '— приховано —';
      const valueMarkup = `<span class="trait-value">${displayValue}</span>`;
      const separator = options.compact ? ': ' : '';
      return `<li class="${classes.join(' ')}">${labelMarkup}${separator}${valueMarkup}</li>`;
    })
    .join('');
};
const updateLobbyInfo = () => {
  if (!state.host.code) {
    ui.lobbyRoomInfo?.classList.add('hidden');
    if (ui.lobbyRoomCode) ui.lobbyRoomCode.textContent = '— — — — —';
    return;
  }
  ui.lobbyRoomInfo?.classList.remove('hidden');
  ui.lobbyRoomCode.textContent = state.host.code.split('').join(' ');
  ui.lobbyRevealProgress.textContent = Math.min(state.revealStage, state.traitSequence.length);
  ui.lobbyRevealTotal.textContent = state.traitSequence.length;
};

const updateScenario = () => {
  const { scenario, bunker } = state;
  if (!ui.host.panel) return;
  if (!scenario) {
    ui.host.scenarioTitle.textContent = '';
    ui.host.scenarioSummary.textContent = '';
    ui.host.scenarioFlavor.innerHTML = '';
    ui.host.bunkerSize.textContent = '—';
    ui.host.bunkerSupplies.textContent = '—';
    ui.host.bunkerSpecial.textContent = '—';
    return;
  }
  ui.host.scenarioTitle.textContent = scenario.title;
  ui.host.scenarioSummary.textContent = scenario.summary;
  ui.host.scenarioFlavor.innerHTML = (scenario.flavor || [])
    .map((item) => `<li>${item}</li>`)
    .join('');
  ui.host.bunkerSize.textContent = bunker?.size || '—';
  ui.host.bunkerSupplies.textContent = bunker?.supplies || '—';
  ui.host.bunkerSpecial.textContent = bunker?.special || '—';
};

const updateRevealUI = () => {
  const unlocked = Math.min(state.revealStage, state.traitSequence.length);
  const total = state.traitSequence.length;
  if (ui.host.revealTrack) {
    ui.host.revealTrack.style.setProperty('--progress', total ? `${(unlocked / total) * 100}%` : '0%');
  }
  if (ui.host.revealLabel) {
    const currentKey = state.traitSequence[Math.max(0, unlocked - 1)];
    const nextKey = state.traitSequence[unlocked];
    if (unlocked === 0) {
      ui.host.revealLabel.textContent = `Очікує: ${traitLabels[state.traitSequence[0]] || '—'}`;
    } else if (unlocked >= total) {
      ui.host.revealLabel.textContent = `Усі риси відкрито (${total})`;
    } else {
      const openedLabel = traitLabels[currentKey] || currentKey || '—';
      const upcomingLabel = traitLabels[nextKey] || nextKey || '—';
      ui.host.revealLabel.textContent = `Відкрито: ${openedLabel} → Далі: ${upcomingLabel}`;
    }
  }
  if (ui.player.traits) {
    ui.player.traits.innerHTML = buildTraitList(
      state.player.profile,
      state.revealStage,
      state.traitSequence
    );
  }
  updateLobbyInfo();
};

const updateHostGrid = (players) => {
  if (!ui.host.grid) return;
  ui.host.grid.innerHTML = '';
  const template = ui.hostCardTemplate?.content?.firstElementChild;
  players.forEach((player) => {
    const card = template ? template.cloneNode(true) : document.createElement('article');
    card.classList.add('mini-card');
    card.dataset.connected = player.connected ? 'true' : 'false';
    const slotLabel = card.querySelector('[data-slot]');
    const statusLabel = card.querySelector('[data-status]');
    const nameLabel = card.querySelector('[data-name]');
    const traitsList = card.querySelector('[data-mini-traits]');
    if (slotLabel) slotLabel.textContent = `Слот ${player.slot + 1}`;
    if (statusLabel) statusLabel.textContent = player.connected ? 'online' : 'очікує';
    if (nameLabel) nameLabel.textContent = player.name || `Гравець ${player.slot + 1}`;
    if (traitsList) {
      traitsList.innerHTML = buildTraitList(player.profile, state.revealStage, state.traitSequence, {
        compact: true,
        revealAll: true
      });
    }
    ui.host.grid.appendChild(card);
  });
};

const applyHostState = (payload) => {
  state.role = 'host';
  state.host.code = payload.code;
  state.scenario = payload.scenario;
  state.bunker = payload.bunker;
  state.revealStage = payload.revealStage ?? 0;
  state.traitSequence = payload.traitSequence ?? state.traitSequence;
  ui.host.code.textContent = payload.code.split('').join(' ');
  updateScenario();
  updateRevealUI();
  updateHostGrid(payload.players || []);
};

const applyPlayerState = (payload) => {
  state.role = 'player';
  state.player.code = payload.code;
  state.player.name = payload.name;
  state.player.profile = payload.profile;
  state.player.slot = payload.slot;
  state.scenario = payload.scenario;
  state.bunker = payload.bunker;
  state.revealStage = payload.revealStage ?? 0;
  state.traitSequence = payload.traitSequence ?? state.traitSequence;
  ui.player.code.textContent = payload.code?.split('').join(' ') || '';
  ui.player.name.textContent = payload.name || `Гравець ${Number(payload.slot) + 1}`;
  ui.player.callSign.textContent = payload.profile?.callSign || '—';
  ui.player.age.textContent = payload.profile?.age ? `${payload.profile.age} років` : '';
  updateRevealUI();
};

const connectHostEvents = () => {
  if (!state.host.code || !state.host.token) return;
  if (state.host.events) { state.host.events.close(); trackConnection(false); }
  const url = new URL('/events', window.location.origin);
  url.searchParams.set('role', 'host');
  url.searchParams.set('code', state.host.code);
  url.searchParams.set('token', state.host.token);
  const events = new EventSource(url);
  state.host.events = events;
  events.onopen = () => trackConnection(true);
  events.onerror = () => {
    trackConnection(false);
    showToast('Втрачено зв\'язок із сервером. Спроба перепідключення…', 4000);
  };
  events.addEventListener('ready', (event) => {
    const data = safeParse(event.data);
    if (data) applyHostState(data);
  });
  events.addEventListener('state', (event) => {
    const data = safeParse(event.data);
    if (data) applyHostState(data);
  });
  events.addEventListener('error', (event) => {
    const data = safeParse(event.data);
    if (data?.message) showToast(data.message, 4500);
  });
};

const connectPlayerEvents = () => {
  if (!state.player.code || !state.player.token) return;
  if (state.player.events) { state.player.events.close(); trackConnection(false); }
  const url = new URL('/events', window.location.origin);
  url.searchParams.set('role', 'player');
  url.searchParams.set('code', state.player.code);
  url.searchParams.set('token', state.player.token);
  const events = new EventSource(url);
  state.player.events = events;
  events.onopen = () => trackConnection(true);
  events.onerror = () => {
    trackConnection(false);
    showToast('З\'єднання втрачено. Очікуємо перепідключення…', 4200);
  };
  events.addEventListener('ready', (event) => {
    const data = safeParse(event.data);
    if (data) applyPlayerState(data);
  });
  events.addEventListener('state', (event) => {
    const data = safeParse(event.data);
    if (data) applyPlayerState(data);
  });
  events.addEventListener('redirect', (event) => {
    const data = safeParse(event.data);
    if (data?.message) showToast(data.message, 5000);
    resetToLobby();
  });
  events.addEventListener('error', (event) => {
    const data = safeParse(event.data);
    if (data?.message) showToast(data.message, 4500);
  });
};

const safeParse = (input) => {
  try {
    return JSON.parse(input);
  } catch (error) {
    return null;
  }
};

const initCamera = async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    ui.player.overlay.textContent = 'Браузер не підтримує відеозахоплення.';
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    ui.player.video.srcObject = stream;
    ui.player.overlay.classList.add('hidden');
  } catch (error) {
    ui.player.overlay.textContent = 'Камеру заблоковано. Дозволь доступ, щоб бачити себе на картці.';
  }
};

const resetToLobby = () => {
  state.role = 'guest';
  if (state.player.events) {
    state.player.events.close();
    trackConnection(false);
  }
  if (state.host.events) {
    state.host.events.close();
    trackConnection(false);
  }
  state.player = { code: null, token: null, slot: null, profile: null, name: null, events: null };
  state.host = { code: null, token: null, events: null };
  if (ui.host.code) ui.host.code.textContent = '';
  state.traitSequence = [];
  state.scenario = null;
  state.bunker = null;
  state.revealStage = 0;
  updateLobbyInfo();
  updateScenario();
  updateRevealUI();
  showSection('lobby');
};

const request = async (url, payload) => {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || 'Помилка запиту');
  }
  return response.json();
};

ui.createRoom?.addEventListener('click', async () => {
  try {
    const payload = await request('/host/create-room');
    state.role = 'host';
    state.host.code = payload.code;
    state.host.token = payload.hostToken;
    state.traitSequence = payload.traitSequence || [];
    state.revealStage = payload.revealStage ?? 0;
    state.scenario = payload.scenario;
    state.bunker = payload.bunker;
    updateLobbyInfo();
    updateScenario();
    updateRevealUI();
    ui.host.code.textContent = payload.code.split('').join(' ');
    const initialPlayers = (payload.players || []).map((item) => ({
      slot: item.slot,
      name: null,
      connected: false,
      profile: item.profile
    }));
    if (initialPlayers.length) {
      updateHostGrid(initialPlayers);
    }
    showSection('host');
    connectHostEvents();
    showToast('Кімнату створено. Поділись кодом із гравцями.');
  } catch (error) {
    showToast(error.message || 'Не вдалося створити кімнату.');
  }
});

ui.host.revealNext?.addEventListener('click', async () => {
  if (!state.host.token || !state.host.code) return;
  try {
    const result = await request('/host/reveal-next', {
      hostToken: state.host.token,
      code: state.host.code
    });
    state.revealStage = result.revealStage;
    updateRevealUI();
  } catch (error) {
    showToast(error.message || 'Не вдалося оновити етап.');
  }
});

ui.host.resetReveal?.addEventListener('click', async () => {
  if (!state.host.token || !state.host.code) return;
  try {
    const result = await request('/host/reset-reveal', {
      hostToken: state.host.token,
      code: state.host.code
    });
    state.revealStage = result.revealStage;
    updateRevealUI();
  } catch (error) {
    showToast(error.message || 'Не вдалося скинути стан.');
  }
});

ui.joinForm?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const code = uppercaseCode(formData.get('code'));
  const name = formData.get('name');
  if (!code) {
    showToast('Введи код кімнати.');
    return;
  }
  try {
    const payload = await request('/player/join', { code, name });
    state.player.code = code;
    state.player.token = payload.token;
    state.player.profile = payload.profile;
    state.player.slot = payload.slot;
    state.traitSequence = payload.traitSequence || [];
    state.revealStage = payload.revealStage ?? 0;
    state.player.name = name;
    state.role = 'player';
    applyPlayerState({ ...payload, code, name });
    showSection('player');
    connectPlayerEvents();
    initCamera();
    showToast('Ти в команді. Очікуй сигнал ведучого.');
  } catch (error) {
    showToast(error.message || 'Не вдалося приєднатись.');
  }
});

window.addEventListener('beforeunload', () => {
  if (state.role === 'player' && state.player.token) {
    const body = JSON.stringify({ token: state.player.token });
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/player/leave', new Blob([body], { type: 'application/json' }));
    } else {
      fetch('/player/leave', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true });
    }
  }
  if (state.role === 'host' && state.host.token && state.host.code) {
    const body = JSON.stringify({ hostToken: state.host.token, code: state.host.code });
    if (navigator.sendBeacon) {
      navigator.sendBeacon('/host/close-room', new Blob([body], { type: 'application/json' }));
    } else {
      fetch('/host/close-room', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body, keepalive: true });
    }
  }
});

showSection('lobby');
updateLobbyInfo();
