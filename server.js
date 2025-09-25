import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

import {
  catastrophePrompts,
  bunkerDetails,
  archetypeSeeds,
  aiPhrases
} from './data.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 3000;
const MAX_PLAYERS = 8;
const TRAIT_SEQUENCE = [
  'profession',
  'skill',
  'personality',
  'health',
  'hobby',
  'baggage',
  'fear',
  'twist',
  'synthetic'
];

const randomChoice = (array) => array[Math.floor(Math.random() * array.length)];
const cryptoRandomInt = (max) => crypto.randomInt(0, Math.max(max, 1));

class AIOracle {
  constructor(seeds) {
    this.seeds = seeds;
  }

  generateProfile() {
    const profile = Object.fromEntries(
      Object.entries(this.seeds).map(([key, seed]) => [
        key,
        Array.isArray(seed) && seed.length ? seed[cryptoRandomInt(seed.length)] : ''
      ])
    );
    profile.synthetic = this.composeStory(profile);
    profile.age = 18 + cryptoRandomInt(32);
    profile.callSign = this.createCallSign(profile);
    return profile;
  }

  createCallSign(profile) {
    const adjective = randomChoice([
      'Кристал',
      'Геліос',
      'Азимут',
      'Вектор',
      'Фрактал',
      'Норд',
      'Графіт',
      'Комета'
    ]);
    const noun = profile.profession?.split(' ')[0] || 'Лідер';
    return `${adjective}-${noun.toUpperCase()}`;
  }

  composeStory(profile) {
    const opening = randomChoice(aiPhrases.openings);
    const connector = randomChoice(aiPhrases.connectors);
    const ending = randomChoice(aiPhrases.endings);
    const detail = shuffleSentence([
      profile.skill,
      profile.personality,
      profile.baggage,
      profile.twist
    ]);
    return `${opening}: ${detail}, де ${connector}, ${ending}`;
  }
}

const shuffleSentence = (fragments) => {
  const copy = fragments.filter(Boolean);
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = cryptoRandomInt(i + 1);
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.join(', ').replace(/, ([^,]*)$/, ' і $1');
};

const rooms = new Map();
const oracle = new AIOracle(archetypeSeeds);

const createRoomCode = () => {
  const alphabet = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
  let code = '';
  for (let i = 0; i < 5; i += 1) {
    code += alphabet[cryptoRandomInt(alphabet.length)];
  }
  return code;
};

const createRoom = () => {
  const scenario = randomChoice(catastrophePrompts);
  const bunker = randomChoice(bunkerDetails);
  const players = Array.from({ length: MAX_PLAYERS }, (_, index) => ({
    slot: index,
    profile: oracle.generateProfile(),
    name: null,
    token: null,
    connected: false,
    streamOpen: false
  }));
  return {
    code: createRoomCode(),
    scenario,
    bunker,
    revealStage: 0,
    host: {
      token: crypto.randomUUID(),
      connection: null
    },
    players
  };
};

const getHostState = (room) => ({
  code: room.code,
  scenario: room.scenario,
  bunker: room.bunker,
  revealStage: room.revealStage,
  traitSequence: TRAIT_SEQUENCE,
  players: room.players.map((player) => ({
    slot: player.slot,
    name: player.name,
    connected: player.connected,
    profile: player.profile
  }))
});

const getPlayerState = (room, slot) => {
  const player = room.players[slot];
  return {
    code: room.code,
    scenario: room.scenario,
    bunker: room.bunker,
    revealStage: room.revealStage,
    traitSequence: TRAIT_SEQUENCE,
    slot,
    name: player?.name,
    profile: player?.profile
  };
};

const sendEvent = (res, event, payload) => {
  if (!res) return;
  res.write(`event: ${event}\n`);
  res.write(`data: ${JSON.stringify(payload)}\n\n`);
};

const closeConnection = (res) => {
  try {
    res.end();
  } catch (error) {
    // ignore
  }
};

const broadcastRoom = (room) => {
  if (room.host.connection) {
    sendEvent(room.host.connection, 'state', getHostState(room));
  }
  room.players.forEach((player) => {
    if (player.connection) {
      sendEvent(player.connection, 'state', getPlayerState(room, player.slot));
    }
  });
};

const findRoomByHostToken = (token) => {
  for (const room of rooms.values()) {
    if (room.host.token === token) return room;
  }
  return null;
};

const findRoomByPlayerToken = (token) => {
  for (const room of rooms.values()) {
    const match = room.players.find((player) => player.token === token);
    if (match) {
      return { room, player: match };
    }
  }
  return null;
};

const removeRoom = (code) => {
  const room = rooms.get(code);
  if (!room) return;
  rooms.delete(code);
  closeConnection(room.host.connection);
  room.players.forEach((player) => closeConnection(player.connection));
};

const readJson = async (req) => {
  const chunks = [];
  for await (const chunk of req) {
    chunks.push(chunk);
  }
  if (!chunks.length) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch (error) {
    return null;
  }
};

const respondJson = (res, statusCode, payload) => {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache'
  });
  res.end(JSON.stringify(payload));
};

const serveStatic = (req, res, pathname) => {
  const filePath = path.join(__dirname, pathname === '/' ? '/index.html' : pathname);
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('Not found');
      return;
    }
    const ext = path.extname(filePath);
    const map = {
      '.html': 'text/html',
      '.css': 'text/css',
      '.js': 'application/javascript',
      '.json': 'application/json',
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.svg': 'image/svg+xml'
    };
    res.writeHead(200, { 'Content-Type': map[ext] || 'application/octet-stream' });
    res.end(data);
  });
};

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);
  const { pathname, searchParams } = url;

  if (req.method === 'GET' && pathname === '/events') {
    const code = (searchParams.get('code') || '').toUpperCase();
    const role = searchParams.get('role');
    const token = searchParams.get('token');

    res.writeHead(200, {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive'
    });
    res.write('\n');

    if (role === 'host') {
      const room = rooms.get(code);
      if (!room || room.host.token !== token) {
        sendEvent(res, 'error', { message: 'Недійсний токен ведучого або код кімнати.' });
        closeConnection(res);
        return;
      }
      room.host.connection = res;
      sendEvent(res, 'ready', getHostState(room));
      broadcastRoom(room);
      req.on('close', () => {
        room.host.connection = null;
      });
      return;
    }

    if (role === 'player') {
      const result = findRoomByPlayerToken(token);
      if (!result || result.room.code !== code) {
        sendEvent(res, 'error', { message: 'Недійсний доступ гравця.' });
        closeConnection(res);
        return;
      }
      const { room, player } = result;
      player.connection = res;
      player.connected = true;
      sendEvent(res, 'ready', getPlayerState(room, player.slot));
      broadcastRoom(room);
      req.on('close', () => {
        player.connection = null;
        player.connected = false;
        broadcastRoom(room);
      });
      return;
    }

    sendEvent(res, 'error', { message: 'Невідомий тип підключення.' });
    closeConnection(res);
    return;
  }

  if (req.method === 'POST' && pathname === '/host/create-room') {
    const room = createRoom();
    rooms.set(room.code, room);
    respondJson(res, 200, {
      code: room.code,
      hostToken: room.host.token,
      scenario: room.scenario,
      bunker: room.bunker,
      revealStage: room.revealStage,
      traitSequence: TRAIT_SEQUENCE,
      players: room.players.map(({ slot, profile }) => ({ slot, profile }))
    });
    return;
  }

  if (req.method === 'POST' && pathname === '/host/reveal-next') {
    const payload = await readJson(req);
    if (!payload) {
      respondJson(res, 400, { message: 'Неможливо обробити запит.' });
      return;
    }
    const hostToken = payload.hostToken;
    const code = String(payload.code || '').trim().toUpperCase();
    const room = rooms.get(code);
    if (!room || room.host.token !== hostToken) {
      respondJson(res, 403, { message: 'Доступ заборонено.' });
      return;
    }
    if (room.revealStage < TRAIT_SEQUENCE.length) {
      room.revealStage += 1;
      broadcastRoom(room);
    }
    respondJson(res, 200, { revealStage: room.revealStage });
    return;
  }

  if (req.method === 'POST' && pathname === '/host/reset-reveal') {
    const payload = await readJson(req);
    if (!payload) {
      respondJson(res, 400, { message: 'Неможливо обробити запит.' });
      return;
    }
    const hostToken = payload.hostToken;
    const code = String(payload.code || '').trim().toUpperCase();
    const room = rooms.get(code);
    if (!room || room.host.token !== hostToken) {
      respondJson(res, 403, { message: 'Доступ заборонено.' });
      return;
    }
    room.revealStage = 0;
    broadcastRoom(room);
    respondJson(res, 200, { revealStage: room.revealStage });
    return;
  }

  if (req.method === 'POST' && pathname === '/player/join') {
    const payload = await readJson(req);
    if (!payload) {
      respondJson(res, 400, { message: 'Неможливо обробити запит.' });
      return;
    }
    const code = String(payload.code || '').trim().toUpperCase();
    const name = payload.name;
    const room = rooms.get(code);
    if (!room) {
      respondJson(res, 404, { message: 'Кімнату не знайдено.' });
      return;
    }
    const slot = room.players.find((player) => player.token === null);
    if (!slot) {
      respondJson(res, 409, { message: 'У кімнаті немає вільних місць.' });
      return;
    }
    slot.name = String(name || '').trim() || `Гравець ${slot.slot + 1}`;
    slot.token = crypto.randomUUID();
    respondJson(res, 200, {
      token: slot.token,
      slot: slot.slot,
      scenario: room.scenario,
      bunker: room.bunker,
      revealStage: room.revealStage,
      traitSequence: TRAIT_SEQUENCE,
      profile: slot.profile
    });
    broadcastRoom(room);
    return;
  }

  if (req.method === 'POST' && pathname === '/player/leave') {
    const payload = await readJson(req);
    if (!payload) {
      respondJson(res, 400, { message: 'Неможливо обробити запит.' });
      return;
    }
    const { token } = payload;
    const result = findRoomByPlayerToken(token);
    if (!result) {
      respondJson(res, 404, { message: 'Гравця не знайдено.' });
      return;
    }
    const { room, player } = result;
    if (player.connection) {
      sendEvent(player.connection, 'redirect', { message: 'Ви залишили кімнату.' });
      closeConnection(player.connection);
    }
    player.name = null;
    player.token = null;
    player.connection = null;
    player.connected = false;
    respondJson(res, 200, { success: true });
    broadcastRoom(room);
    return;
  }

  if (req.method === 'POST' && pathname === '/host/close-room') {
    const payload = await readJson(req);
    if (!payload) {
      respondJson(res, 400, { message: 'Неможливо обробити запит.' });
      return;
    }
    const hostToken = payload.hostToken;
    const code = String(payload.code || '').trim().toUpperCase();
    const room = rooms.get(code);
    if (!room || room.host.token !== hostToken) {
      respondJson(res, 403, { message: 'Доступ заборонено.' });
      return;
    }
    room.players.forEach((player) => {
      if (player.connection) {
        sendEvent(player.connection, 'redirect', { message: 'Сесію завершено ведучим.' });
      }
    });
    removeRoom(code);
    respondJson(res, 200, { success: true });
    return;
  }

  if (req.method === 'GET' && pathname.startsWith('/health')) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok' }));
    return;
  }

  serveStatic(req, res, pathname);
});

server.listen(PORT, () => {
  console.log(`Bunker server listening on http://localhost:${PORT}`);
});
