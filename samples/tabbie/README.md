# Tabbie — Web Control Server

Web app that controls your Tabbie desk companion over WiFi. Change expressions, send notifications, and run pomodoro timers from your browser.

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --host 0.0.0.0
```

Open `http://localhost:8000` in your browser.

## Firmware

The Pico firmware lives in `upython/samples/`. Before flashing:

1. Edit `upython/samples/config.py` with your WiFi credentials and this server's IP
2. Flash the `upython/` directory to the Pico via PyCharm's MicroPython plugin (F5)
3. Boot the Pico — it connects to WiFi and polls this server every ~3s

## API

| Method | Path | Body | Description |
|--------|------|------|-------------|
| `GET` | `/api/poll` | — | Returns and clears pending commands (called by Pico) |
| `POST` | `/api/expression` | `{"expression": "love"}` | Queue an expression change |
| `POST` | `/api/notify` | `{"text": "Hello!"}` | Queue a text notification |
| `POST` | `/api/pomodoro/start` | `{"task": "Study", "duration": 25}` | Start a pomodoro timer |
| `POST` | `/api/pomodoro/stop` | — | Stop the pomodoro timer |
| `GET` | `/api/pomodoro/status` | — | Current pomodoro state + countdown |

### Expressions

`idle`, `focus`, `break_time`, `love`, `angry`, `complete`

### Pomodoro Flow

Start → focus phase (default 25min) → auto-transitions to break (5min) → completes back to idle. The web UI shows a live countdown.
