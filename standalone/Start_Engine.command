#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  AI Sound Design Engine — Standalone Launcher                   ║
# ║  Double-click to start. No Python installation needed.          ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/.engine.pid"
PORT=8000

clear
echo "╔══════════════════════════════════════════╗"
echo "║   AI Sound Design Engine v0              ║"
echo "║   Starting...                            ║"
echo "╚══════════════════════════════════════════╝"
echo ""

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

# ── Start the bundled executable ──────────────────────────────────
EXECUTABLE="$SCRIPT_DIR/AI_Preset_Engine"
if [ ! -f "$EXECUTABLE" ]; then
    echo "❌ Executable not found: $EXECUTABLE"
    echo "   Make sure Start_Engine.command is in the same folder as AI_Preset_Engine."
    echo ""
    echo "Press any key to close..."
    read -n 1
    exit 1
fi

echo "→ Starting engine..."
"$EXECUTABLE" &
SERVER_PID=$!
echo "$SERVER_PID" > "$PID_FILE"

# ── Wait for server to be ready ───────────────────────────────────
echo "→ Waiting for server..."
for i in $(seq 1 20); do
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
    echo "  Max bridge: POST http://127.0.0.1:$PORT/api/retrieve"
    echo ""
    echo "  Open Ableton → load max_bridge/AI_Preset_Engine.maxpat"
    echo ""
    echo "  To stop: double-click Stop_Engine.command"
    echo "           or close this window"
    echo ""
    echo "Press any key to close this window (server keeps running)..."
    read -n 1
else
    echo ""
    echo "❌ Server failed to start within 20 seconds."
    echo ""
    echo "Press any key to close..."
    read -n 1
    kill "$SERVER_PID" 2>/dev/null
    rm -f "$PID_FILE"
    exit 1
fi
