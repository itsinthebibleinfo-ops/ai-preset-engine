#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  AI Sound Design Engine — Stop Server                           ║
# ║  Double-click this file to stop the backend.                    ║
# ╚══════════════════════════════════════════════════════════════════╝

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/.engine.pid"
PORT=8000

echo ""
echo "Stopping AI Sound Design Engine..."
echo ""

STOPPED=false

# ── Try PID file first ────────────────────────────────────────────
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null
        echo "✓ Server stopped (PID $PID)"
        STOPPED=true
    fi
    rm -f "$PID_FILE"
fi

# ── Fallback: kill anything on the port ───────────────────────────
if ! $STOPPED; then
    PIDS=$(lsof -ti:$PORT 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill 2>/dev/null
        echo "✓ Server stopped (port $PORT)"
        STOPPED=true
    fi
fi

if $STOPPED; then
    echo ""
    echo "Engine is stopped. You can close this window."
else
    echo "No running engine found."
fi

echo ""
echo "Press any key to close..."
read -n 1
