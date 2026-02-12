"""FastAPI web server for Tiny Entities simulation"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Set

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Tiny Entities Web")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ── Global simulation state ───────────────────────────────────────────────────

class SimulationState:
    def __init__(self):
        self.sim = None
        self.running = False
        self.paused = False
        self.clients: Set[WebSocket] = set()

    def is_ready(self):
        return self.sim is not None


state = SimulationState()


# ── Serialization ─────────────────────────────────────────────────────────────

def serialize_state(sim) -> dict:
    """Build a compact JSON-serializable snapshot of current sim state."""
    world = sim.world_model.world

    # Grid as flat list (0=empty, 1=food, 2=obstacle)
    grid = world.grid.tolist()

    # Sound: only send non-silent cells as sparse [{x,y,freq,amp}]
    sounds = []
    amps = world.sound_grid[:, :, 1]
    for y, x in zip(*np.where(amps > 0.01)):
        sounds.append({
            "x": int(x), "y": int(y),
            "freq": round(float(world.sound_grid[y, x, 0]), 2),
            "amp": round(float(world.sound_grid[y, x, 1]), 2),
        })

    # Creatures: only what the frontend needs
    creatures = []
    for c in sim.creatures:
        brain = c["brain"]
        creatures.append({
            "id": c["id"],
            "x": int(c["position"][0]),
            "y": int(c["position"][1]),
            "alive": c["alive"],
            "valence": round(float(brain.mood_system.valence), 3),
            "arousal": round(float(brain.mood_system.arousal), 3),
            "health": round(float(brain.health), 1),
            "energy": round(float(brain.energy), 1),
        })

    # Recent thoughts (last 8)
    reflections = sim.reflection_log[-8:]

    # Recent sounds for pattern panel (last 50, strip waveform)
    recent_sounds = [
        {k: v for k, v in s.items() if k not in ("waveform", "sample_rate")}
        for s in sim.sound_history[-50:]
    ]

    alive = sum(1 for c in sim.creatures if c["alive"])

    return {
        "step": sim.step_count,
        "max_steps": sim.max_steps,
        "world": {"width": world.width, "height": world.height},
        "grid": grid,
        "sounds": sounds,
        "creatures": creatures,
        "reflections": reflections,
        "recent_sounds": recent_sounds,
        "stats": {
            "alive": alive,
            "total": len(sim.creatures),
            "total_sounds": len(sim.sound_history),
            "total_thoughts": len(sim.reflection_log),
        },
    }


# ── WebSocket broadcast ───────────────────────────────────────────────────────

async def broadcast(msg: dict):
    """Send message to all connected clients."""
    dead = set()
    text = json.dumps(msg)
    for ws in state.clients:
        try:
            await ws.send_text(text)
        except Exception:
            dead.add(ws)
    state.clients -= dead


# ── Simulation loop ───────────────────────────────────────────────────────────

async def run_loop():
    """Main simulation loop - runs steps and broadcasts state."""
    if not state.sim:
        return
    sim = state.sim
    state.running = True

    while state.running and sim.step_count < sim.max_steps:
        if state.paused:
            await asyncio.sleep(0.05)
            continue

        # One simulation step
        await sim.simulation_step()

        # Periodic LLM analysis
        if sim.step_count % sim.analyze_every == 0 and sim.step_count > 0:
            asyncio.create_task(sim.analyze_emergence())

        # Broadcast state every step if clients connected
        if state.clients:
            await broadcast(serialize_state(sim))

        # Check termination
        if not any(c["alive"] for c in sim.creatures):
            await broadcast({"type": "extinct", "step": sim.step_count})
            break

        # Yield to event loop so WS messages can be received
        await asyncio.sleep(0)

    state.running = False
    if state.clients:
        await broadcast({"type": "done", "step": sim.step_count})


# ── HTTP endpoints ────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    return (STATIC_DIR / "index.html").read_text()


@app.post("/start")
async def start_sim(creatures: int = 12, steps: int = 10000, config: Optional[str] = None):
    """Start a new simulation."""
    if state.running:
        state.running = False
        await asyncio.sleep(0.1)

    from ..simulation.main_loop import EmergentLifeSimulation
    from ..config.config_schema import SimulationConfig

    cfg = None
    if config:
        cfg = SimulationConfig.from_yaml(Path(config))

    state.sim = EmergentLifeSimulation(
        num_creatures=creatures,
        max_steps=steps,
        config=cfg,
    )
    state.paused = False

    asyncio.create_task(run_loop())

    return {
        "status": "started",
        "creatures": creatures,
        "steps": steps,
        "world": {
            "width": state.sim.world_model.world.width,
            "height": state.sim.world_model.world.height,
        },
    }


@app.post("/pause")
async def pause_sim():
    state.paused = not state.paused
    return {"paused": state.paused}


@app.post("/stop")
async def stop_sim():
    state.running = False
    state.paused = False
    return {"status": "stopped"}


@app.get("/state")
async def get_state():
    if not state.sim:
        return {"status": "not_started"}
    return serialize_state(state.sim)


# ── WebSocket endpoint ────────────────────────────────────────────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.clients.add(websocket)
    logger.info(f"Client connected. Total: {len(state.clients)}")

    # Send current state immediately if sim is running
    if state.sim:
        await websocket.send_text(json.dumps(serialize_state(state.sim)))

    try:
        while True:
            msg = await websocket.receive_text()
            cmd = json.loads(msg)
            if cmd.get("action") == "pause":
                state.paused = not state.paused
            elif cmd.get("action") == "stop":
                state.running = False
    except WebSocketDisconnect:
        pass
    finally:
        state.clients.discard(websocket)
        logger.info(f"Client disconnected. Total: {len(state.clients)}")


# ── Standalone entry point ────────────────────────────────────────────────────

def serve(host: str = "0.0.0.0", port: int = 8000, **sim_kwargs):
    """Start the web server and optionally auto-start a simulation."""
    import uvicorn

    async def lifespan():
        if sim_kwargs:
            await start_sim(**sim_kwargs)

    # Auto-start sim if kwargs provided
    if sim_kwargs:
        @app.on_event("startup")
        async def _startup():
            await start_sim(**sim_kwargs)

    uvicorn.run(app, host=host, port=port)
