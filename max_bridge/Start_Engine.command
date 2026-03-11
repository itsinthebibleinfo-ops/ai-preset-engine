#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  AI Sound Design Engine — One-Click Launcher                    ║
# ║  Double-click this file to start the preset engine backend.     ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

# ── Resolve project root (one level up from max_bridge/) ──────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"
PID_FILE="$PROJECT_DIR/.engine.pid"
PORT=8000

clear
echo "╔══════════════════════════════════════════╗"
echo "║   AI Sound Design Engine                 ║"
echo "║   Starting backend server...             ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check Python ──────────────────────────────────────────────────
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "❌ Python not found. Install Python 3.10+ from python.org"
    echo ""
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
echo "✓ Found $PY_VERSION"

# ── Check if server is already running ────────────────────────────
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "✓ Engine already running (PID $OLD_PID)"
        echo ""
        echo "  API: http://127.0.0.1:$PORT"
        echo "  Max bridge: POST http://127.0.0.1:$PORT/api/retrieve"
        echo ""
        echo "Press any key to close this window (server keeps running)..."
        read -n 1
        exit 0
    else
        rm -f "$PID_FILE"
    fi
fi

# ── Create virtual environment if needed ──────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "→ Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
fi

# ── Activate venv ─────────────────────────────────────────────────
source "$VENV_DIR/bin/activate"
echo "✓ Virtual environment activated"

# ── Install dependencies ──────────────────────────────────────────
echo "→ Checking dependencies..."
pip install -q -r "$PROJECT_DIR/requirements.txt" 2>/dev/null
echo "✓ Dependencies ready"

# ── Build unified knowledge if missing ────────────────────────────
KNOWLEDGE="$PROJECT_DIR/sound_lab/output/unified_sound_knowledge.json"
if [ ! -f "$KNOWLEDGE" ]; then
    echo "→ Building unified knowledge database (first run)..."
    $PYTHON -m sound_lab.scripts.build_unified_knowledge
    echo "✓ Knowledge database built"
else
    echo "✓ Knowledge database found"
fi

# ── Start server ──────────────────────────────────────────────────
echo ""
echo "→ Starting server on port $PORT..."
echo ""

cd "$PROJECT_DIR"
uvicorn engine.server:app --host 127.0.0.1 --port $PORT &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

# ── Wait for server to be ready ───────────────────────────────────
echo "→ Waiting for server..."
for i in $(seq 1 15); do
    if curl -s http://127.0.0.1:$PORT/ >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if curl -s http://127.0.0.1:$PORT/ >/dev/null 2>&1; then
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║   ✓ Engine is running!                   ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    echo "  API:        http://127.0.0.1:$PORT"
    echo "  Health:     http://127.0.0.1:$PORT/"
    echo "  Max bridge: POST http://127.0.0.1:$PORT/api/retrieve"
    echo ""
    echo "  Open Ableton → load the Max device → type a prompt!"
    echo ""
    echo "  To stop: double-click Stop_Engine.command"
    echo "           or close this window"
    echo ""
    echo "Press any key to close this window (server keeps running)..."
    read -n 1
else
    echo ""
    echo "❌ Server failed to start. Check the output above for errors."
    echo ""
    echo "Press any key to close..."
    read -n 1
    kill "$SERVER_PID" 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
