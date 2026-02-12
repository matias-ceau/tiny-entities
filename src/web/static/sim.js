/* ── Tiny Entities – WebSocket canvas client ─────────────────────────────── */
'use strict';

const COLORS = {
  empty:    '#0f0f14',
  food:     '#78dc50',
  foodEdge: '#a0ff80',
  obstacle: '#b4503c',
  obsEdge:  '#dc7850',
};

let ws         = null;
let lastState  = null;
let worldW     = 100;
let worldH     = 100;
let cellSize   = 1;

const canvas   = document.getElementById('world-canvas');
const ctx      = canvas.getContext('2d');
let imgData    = null;
let pixels     = null;

/* ── WebSocket ──────────────────────────────────────────────────────────── */

function connect() {
  const url = `ws://${location.host}/ws`;
  ws = new WebSocket(url);

  ws.onopen = () => {
    document.getElementById('stat-conn').classList.add('connected');
  };

  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);

    if (data.type === 'extinct') {
      addSystemMessage('⚠ All creatures have died!');
      return;
    }
    if (data.type === 'done') {
      addSystemMessage(`✅ Simulation complete at step ${data.step}`);
      setButtonState('stopped');
      return;
    }

    lastState = data;
    render(data);
    updatePanels(data);
    updateStats(data);
  };

  ws.onclose = () => {
    document.getElementById('stat-conn').classList.remove('connected');
    setTimeout(connect, 2000);            // auto-reconnect
  };

  ws.onerror = () => ws.close();
}

/* ── Canvas setup ───────────────────────────────────────────────────────── */

function initCanvas(w, h) {
  worldW = w;  worldH = h;

  const wrap   = document.getElementById('world-wrap');
  const maxW   = wrap.clientWidth;
  const maxH   = wrap.clientHeight;
  cellSize     = Math.max(1, Math.min(Math.floor(maxW / w), Math.floor(maxH / h)));

  canvas.width  = w * cellSize;
  canvas.height = h * cellSize;

  imgData = ctx.createImageData(canvas.width, canvas.height);
  pixels  = imgData.data;
}

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

const C_EMPTY    = hexToRgb(COLORS.empty);
const C_FOOD     = hexToRgb(COLORS.food);
const C_OBSTACLE = hexToRgb(COLORS.obstacle);

function setPixelBlock(gx, gy, r, g, b) {
  const px = gx * cellSize, py = gy * cellSize;
  for (let dy = 0; dy < cellSize; dy++) {
    for (let dx = 0; dx < cellSize; dx++) {
      const i = ((py + dy) * canvas.width + (px + dx)) * 4;
      pixels[i]   = r;
      pixels[i+1] = g;
      pixels[i+2] = b;
      pixels[i+3] = 255;
    }
  }
}

/* ── Render ─────────────────────────────────────────────────────────────── */

function render(state) {
  if (!imgData) initCanvas(state.world.width, state.world.height);

  const grid = state.grid;

  // Draw grid cells
  for (let y = 0; y < worldH; y++) {
    for (let x = 0; x < worldW; x++) {
      const v = grid[y][x];
      let c;
      if (v === 1)      c = C_FOOD;
      else if (v === 2) c = C_OBSTACLE;
      else              c = C_EMPTY;
      setPixelBlock(x, y, c[0], c[1], c[2]);
    }
  }

  ctx.putImageData(imgData, 0, 0);

  // Sound overlay
  if (state.sounds.length > 0) {
    for (const s of state.sounds) {
      const alpha = Math.min(s.amp * 0.6, 0.5);
      const color = s.freq < 0.5 ? '80,150,255' : '255,100,100';
      ctx.fillStyle = `rgba(${color},${alpha})`;
      ctx.fillRect(s.x * cellSize, s.y * cellSize, cellSize, cellSize);
    }
  }

  // Food outline (draw borders on food cells if cellSize > 2)
  if (cellSize > 3) {
    ctx.strokeStyle = COLORS.foodEdge;
    ctx.lineWidth = 1;
    for (let y = 0; y < worldH; y++) {
      for (let x = 0; x < worldW; x++) {
        if (grid[y][x] === 1) {
          ctx.strokeRect(x * cellSize + 0.5, y * cellSize + 0.5, cellSize - 1, cellSize - 1);
        }
      }
    }
  }

  // Creatures
  for (const c of state.creatures) {
    if (!c.alive) continue;

    const cx = c.x * cellSize + cellSize / 2;
    const cy = c.y * cellSize + cellSize / 2;
    const r  = Math.max(cellSize / 2.5, 3);

    // Mood-driven color (same formula as pygame visualizer)
    const base = 150, range = 105;
    const rr   = clamp(base + c.arousal * range, 0, 255);
    let gr, br;
    if (c.valence > 0) {
      gr = clamp(base + c.valence * range, 0, 255);
      br = clamp(base - c.valence * 50,   0, 255);
    } else {
      gr = clamp(base + c.valence * 50,   0, 255);
      br = clamp(base - c.valence * range, 0, 255);
    }
    const color = `rgb(${Math.round(rr)},${Math.round(gr)},${Math.round(br)})`;

    // White outline
    ctx.beginPath();
    ctx.arc(cx, cy, r + 2, 0, Math.PI * 2);
    ctx.fillStyle = '#ffffff';
    ctx.fill();

    // Creature body
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();

    // Health/energy bars (when cell is big enough)
    if (cellSize >= 6) {
      const bw = cellSize - 2;
      const bh = 2;
      const bx = c.x * cellSize + 1;
      const by = c.y * cellSize - 6;

      // HP bar
      ctx.fillStyle = '#333';
      ctx.fillRect(bx, by, bw, bh);
      ctx.fillStyle = '#4cff88';
      ctx.fillRect(bx, by, bw * (c.health / 100), bh);

      // Energy bar
      ctx.fillStyle = '#333';
      ctx.fillRect(bx, by + 3, bw, bh);
      ctx.fillStyle = '#ffc850';
      ctx.fillRect(bx, by + 3, bw * (c.energy / 100), bh);
    }
  }
}

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

/* ── Panel updates ──────────────────────────────────────────────────────── */

// Thoughts panel - keep track of shown steps to avoid dupe appends
let lastThoughtStep = -1;

function updatePanels(state) {
  updateThoughts(state.reflections);
  updatePatterns(state.recent_sounds, state.creatures);
  updateCreatures(state.creatures);
}

function updateThoughts(reflections) {
  const body = document.getElementById('thoughts-body');
  if (!reflections || reflections.length === 0) return;

  // Only re-render if new thoughts arrived
  const newest = reflections[reflections.length - 1];
  if (newest.step === lastThoughtStep) return;
  lastThoughtStep = newest.step;

  body.innerHTML = '';
  for (const r of [...reflections].reverse()) {
    const el = document.createElement('div');
    el.className = 'thought-entry';
    el.innerHTML = `<div class="thought-meta">${r.creature_id} · step ${r.step}</div>
                    <div class="thought-text">${escHtml(r.text)}</div>`;
    body.appendChild(el);
  }
}

function updatePatterns(sounds, creatures) {
  const body = document.getElementById('patterns-body');
  if (!sounds || sounds.length < 3) return;

  // Active communicators
  const unique = new Set(sounds.map(s => s.creature_id)).size;
  const lowF   = sounds.filter(s => s.frequency < 0.5).length;
  const highF  = sounds.length - lowF;

  // Rhythm detection
  let rhythmAlert = '';
  if (sounds.length > 10) {
    const diffs = [];
    for (let i = 1; i < Math.min(sounds.length, 20); i++) {
      diffs.push(sounds[i].step - sounds[i-1].step);
    }
    const avg = mean(diffs), std = stddev(diffs, avg);
    if (std < avg * 0.5 && avg > 0) {
      rhythmAlert = `<div class="pattern-alert">⚠ Rhythmic pattern! Interval: ${avg.toFixed(1)} ± ${std.toFixed(1)}</div>`;
    }
  }

  // Group mood
  const alive = creatures.filter(c => c.alive);
  let moodHtml = '';
  if (alive.length > 0) {
    const avgV   = mean(alive.map(c => c.valence));
    const avgA   = mean(alive.map(c => c.arousal));
    const stdV   = stddev(alive.map(c => c.valence), avgV);
    const emoji  = avgV > 0.2 ? '😊' : avgV < -0.2 ? '😔' : '😐';
    const lowVar = stdV < 0.1 ? `<div class="pattern-alert" style="border-color:rgba(255,100,100,.3);color:#ff9090">⚠ Low mood variation</div>` : '';

    moodHtml = `
      <div class="stat-row"><span class="stat-label">Group valence</span><span class="stat-val">${emoji} ${fmt(avgV)}</span></div>
      <div class="stat-row"><span class="stat-label">Group arousal</span><span class="stat-val">${fmt(avgA)}</span></div>
      <div class="stat-row"><span class="stat-label">Mood diversity</span><span class="stat-val">${fmt(stdV)}</span></div>
      ${lowVar}`;
  }

  body.innerHTML = `
    <div class="stat-row"><span class="stat-label">Active communicators</span><span class="stat-val">${unique}</span></div>
    <div class="stat-row"><span class="stat-label">Low freq sounds</span><span class="stat-val">${lowF}</span></div>
    <div class="stat-row"><span class="stat-label">High freq sounds</span><span class="stat-val">${highF}</span></div>
    ${rhythmAlert}
    <br>${moodHtml}`;
}

function updateCreatures(creatures) {
  const body = document.getElementById('creatures-body');
  if (!creatures || creatures.length === 0) return;

  body.innerHTML = creatures.map(c => {
    const base = 150, range = 105;
    const rr = clamp(base + c.arousal * range, 0, 255);
    let gr, br;
    if (c.valence > 0) { gr = clamp(base + c.valence * range, 0, 255); br = clamp(base - c.valence * 50, 0, 255); }
    else               { gr = clamp(base + c.valence * 50, 0, 255);   br = clamp(base - c.valence * range, 0, 255); }
    const color = `rgb(${Math.round(rr)},${Math.round(gr)},${Math.round(br)})`;

    const mood  = c.valence > 0.2 ? '😊' : c.valence < -0.2 ? '😔' : '😐';
    const deathCls = c.alive ? '' : ' creature-dead';

    return `<div class="creature-row${deathCls}">
      <div class="creature-dot" style="background:${color}"></div>
      <div class="creature-info">
        <div class="creature-id">${c.id}${c.alive ? '' : ' 💀'}</div>
        <div class="bar-wrap">
          <div class="bar-bg bar-hp"><div class="bar-fill" style="width:${c.health}%"></div></div>
          <div class="bar-bg bar-en"><div class="bar-fill" style="width:${c.energy}%"></div></div>
        </div>
      </div>
      <span class="mood-pill">${mood} v:${fmt(c.valence)} a:${fmt(c.arousal)}</span>
    </div>`;
  }).join('');
}

function updateStats(state) {
  document.getElementById('stat-step').textContent    = `Step: ${state.step}/${state.max_steps}`;
  document.getElementById('stat-alive').textContent   = `Alive: ${state.stats.alive}/${state.stats.total}`;
  document.getElementById('stat-sounds').textContent  = `Sounds: ${state.stats.total_sounds}`;
  document.getElementById('stat-thoughts').textContent = `Thoughts: ${state.stats.total_thoughts}`;
}

/* ── Controls ───────────────────────────────────────────────────────────── */

async function startSim() {
  const creatures = document.getElementById('inp-creatures').value;
  const steps     = document.getElementById('inp-steps').value;

  await fetch(`/start?creatures=${creatures}&steps=${steps}`, { method: 'POST' });
  setButtonState('running');

  // Re-init canvas on next state message
  imgData = null;
  lastThoughtStep = -1;
}

async function pauseSim() {
  const res  = await fetch('/pause', { method: 'POST' });
  const data = await res.json();
  document.getElementById('btn-pause').textContent = data.paused ? '▶ Resume' : '⏸ Pause';
}

async function stopSim() {
  await fetch('/stop', { method: 'POST' });
  setButtonState('stopped');
}

function setButtonState(s) {
  const btnStart = document.getElementById('btn-start');
  const btnPause = document.getElementById('btn-pause');
  const btnStop  = document.getElementById('btn-stop');
  btnStart.disabled = s === 'running';
  btnPause.disabled = s !== 'running';
  btnStop.disabled  = s !== 'running';
  if (s !== 'running') btnPause.textContent = '⏸ Pause';
}

function togglePanel(name) {
  const body = document.getElementById(`${name}-body`);
  const btn  = body.closest('.panel').querySelector('.toggle');
  const collapsed = body.classList.toggle('collapsed');
  btn.textContent = collapsed ? '+' : '−';
}

function addSystemMessage(msg) {
  const body = document.getElementById('thoughts-body');
  const el   = document.createElement('div');
  el.className = 'pattern-alert';
  el.style.marginBottom = '8px';
  el.textContent = msg;
  body.prepend(el);
}

/* ── Helpers ────────────────────────────────────────────────────────────── */

function mean(arr)          { return arr.length ? arr.reduce((a,b) => a+b, 0) / arr.length : 0; }
function stddev(arr, avg)   { return arr.length ? Math.sqrt(mean(arr.map(x => (x-avg)**2))) : 0; }
function fmt(v)             { return (v >= 0 ? '+' : '') + v.toFixed(2); }
function escHtml(s)         { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

/* ── Resize ─────────────────────────────────────────────────────────────── */

window.addEventListener('resize', () => {
  if (lastState) {
    imgData = null;    // force re-init on next render
    render(lastState);
  }
});

/* ── Boot ───────────────────────────────────────────────────────────────── */

connect();
