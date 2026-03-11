#!/bin/bash
# ╔══════════════════════════════════════════════════════════════════╗
# ║  AI Sound Design Engine — Standalone Build Script               ║
# ║  Creates a self-contained macOS release using PyInstaller.      ║
# ╚══════════════════════════════════════════════════════════════════╝

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_DIR/dist"
RELEASE_NAME="AI_Sound_Design_Engine_v0"
RELEASE_DIR="$DIST_DIR/$RELEASE_NAME"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Building standalone v0...              ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Ensure PyInstaller is available ───────────────────────────────
if ! python3 -m PyInstaller --version &>/dev/null; then
    echo "→ Installing PyInstaller..."
    pip install pyinstaller
fi
echo "✓ PyInstaller $(python3 -m PyInstaller --version 2>&1)"

# ── Clean previous builds ─────────────────────────────────────────
echo "→ Cleaning previous builds..."
rm -rf "$DIST_DIR" "$PROJECT_DIR/build" "$PROJECT_DIR/AI_Preset_Engine.spec"

# ── Run PyInstaller ───────────────────────────────────────────────
echo "→ Running PyInstaller (this may take a minute)..."
cd "$PROJECT_DIR"

python3 -m PyInstaller \
    --name AI_Preset_Engine \
    --onedir \
    --noconfirm \
    --clean \
    --add-data "presets:presets" \
    --add-data "taxonomy:taxonomy" \
    --add-data "sound_lab/output:sound_lab/output" \
    --hidden-import uvicorn.logging \
    --hidden-import uvicorn.loops \
    --hidden-import uvicorn.loops.auto \
    --hidden-import uvicorn.protocols \
    --hidden-import uvicorn.protocols.http \
    --hidden-import uvicorn.protocols.http.auto \
    --hidden-import uvicorn.protocols.http.h11_impl \
    --hidden-import uvicorn.protocols.http.httptools_impl \
    --hidden-import uvicorn.protocols.websockets \
    --hidden-import uvicorn.protocols.websockets.auto \
    --hidden-import uvicorn.protocols.websockets.wsproto_impl \
    --hidden-import uvicorn.lifespan \
    --hidden-import uvicorn.lifespan.on \
    --hidden-import uvicorn.lifespan.off \
    --hidden-import pydantic \
    --hidden-import pydantic.deprecated.decorator \
    --hidden-import email.mime.multipart \
    standalone/entry.py

echo ""
echo "✓ PyInstaller build complete"

# ── Assemble release folder ───────────────────────────────────────
echo "→ Assembling release folder..."
rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# Copy the entire PyInstaller output (executable + _internal/)
cp -R "$DIST_DIR/AI_Preset_Engine/"* "$RELEASE_DIR/"

# Copy Max for Live bridge
mkdir -p "$RELEASE_DIR/max_bridge"
cp "$PROJECT_DIR/max_bridge/AI_Preset_Engine.maxpat" "$RELEASE_DIR/max_bridge/"
cp "$PROJECT_DIR/max_bridge/retrieve_and_apply.js" "$RELEASE_DIR/max_bridge/"

# Copy standalone launcher scripts
cp "$SCRIPT_DIR/Start_Engine.command" "$RELEASE_DIR/"
cp "$SCRIPT_DIR/Stop_Engine.command" "$RELEASE_DIR/"
chmod +x "$RELEASE_DIR/Start_Engine.command"
chmod +x "$RELEASE_DIR/Stop_Engine.command"

# Copy README
if [ -f "$PROJECT_DIR/DEMO_README.md" ]; then
    cp "$PROJECT_DIR/DEMO_README.md" "$RELEASE_DIR/README.md"
fi

# ── Summary ───────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   ✓ Release built successfully!          ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  Location: $RELEASE_DIR"
echo ""
echo "  To test:"
echo "    1. double-click Start_Engine.command"
echo "    2. curl http://127.0.0.1:8000/"
echo "    3. Open Ableton → load max_bridge/AI_Preset_Engine.maxpat"
echo ""
echo "  To distribute: zip the $RELEASE_NAME/ folder."
echo ""
