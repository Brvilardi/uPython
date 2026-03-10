import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

# ── State ────────────────────────────────────────────────────────────────────

command_queue: list[str] = []
current_expression: str = "idle"

pomodoro_state = {
    "active": False,
    "task": "",
    "phase": "idle",          # idle | focus | break
    "start_time": 0.0,
    "focus_duration": 25 * 60,
    "break_duration": 5 * 60,
}

# ── Models ───────────────────────────────────────────────────────────────────

class ExpressionBody(BaseModel):
    expression: str

class NotifyBody(BaseModel):
    text: str

class PomodoroStartBody(BaseModel):
    task: str = ""
    duration: int = 25  # minutes

# ── Helpers ──────────────────────────────────────────────────────────────────

def _check_pomodoro() -> None:
    """Advance pomodoro phase if time is up, queuing commands as needed."""
    if not pomodoro_state["active"]:
        return
    elapsed = time.time() - pomodoro_state["start_time"]

    if pomodoro_state["phase"] == "focus":
        if elapsed >= pomodoro_state["focus_duration"]:
            pomodoro_state["phase"] = "break"
            pomodoro_state["start_time"] = time.time()
            command_queue.append("break_time")
            command_queue.append("notify Break time!")

    elif pomodoro_state["phase"] == "break":
        if elapsed >= pomodoro_state["break_duration"]:
            pomodoro_state["active"] = False
            pomodoro_state["phase"] = "idle"
            command_queue.append("complete")


def _pomodoro_status() -> dict:
    """Build status dict for the web UI."""
    if not pomodoro_state["active"]:
        return {"active": False, "phase": "idle", "task": "", "remaining": 0}

    elapsed = time.time() - pomodoro_state["start_time"]
    if pomodoro_state["phase"] == "focus":
        remaining = max(0, pomodoro_state["focus_duration"] - elapsed)
    else:
        remaining = max(0, pomodoro_state["break_duration"] - elapsed)

    return {
        "active": True,
        "phase": pomodoro_state["phase"],
        "task": pomodoro_state["task"],
        "remaining": int(remaining),
    }

# ── Endpoints ────────────────────────────────────────────────────────────────

STATIC_DIR = Path(__file__).parent / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/poll")
def poll():
    _check_pomodoro()
    cmds = list(command_queue)
    command_queue.clear()
    return {"commands": cmds}


@app.post("/api/expression")
def set_expression(body: ExpressionBody):
    global current_expression
    current_expression = body.expression
    command_queue.append(body.expression)
    return {"ok": True}


@app.post("/api/notify")
def notify(body: NotifyBody):
    command_queue.append(f"notify {body.text}")
    return {"ok": True}


@app.post("/api/pomodoro/start")
def pomodoro_start(body: PomodoroStartBody):
    pomodoro_state["active"] = True
    pomodoro_state["task"] = body.task
    pomodoro_state["phase"] = "focus"
    pomodoro_state["start_time"] = time.time()
    pomodoro_state["focus_duration"] = body.duration * 60
    pomodoro_state["break_duration"] = 5 * 60
    command_queue.append(f"pomodoro {body.task}")
    return {"ok": True}


@app.post("/api/pomodoro/stop")
def pomodoro_stop():
    pomodoro_state["active"] = False
    pomodoro_state["phase"] = "idle"
    command_queue.append("idle")
    return {"ok": True}


@app.get("/api/pomodoro/status")
def pomodoro_status():
    _check_pomodoro()
    return _pomodoro_status()


@app.get("/api/status")
def status():
    """Current state for the web UI (does NOT clear the queue)."""
    _check_pomodoro()
    return {
        "expression": current_expression,
        "queue": list(command_queue),
        "pomodoro": _pomodoro_status(),
    }
