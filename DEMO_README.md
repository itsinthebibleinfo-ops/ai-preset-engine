# AI Sound Design Engine — Demo Guide

## Quick Start (3 Steps)

### 1. Start the Engine
Double-click **`max_bridge/Start_Engine.command`** in Finder.

A Terminal window opens, installs dependencies (first time only), and starts the backend. When you see **"Engine is running!"**, you're good.

### 2. Load the Max Device
- Open Ableton Live
- Load **Wavetable** on any track
- Drag `max_bridge/AI_Preset_Engine.maxpat` onto the same track
  (or open it in Max, save as `.amxd`, then load it)

The device status should show **"Ready — engine connected"**.

### 3. Generate a Preset
- Type a prompt: `warm airy neo soul pad`
- Click **Generate** (or press Enter)
- Click **Apply** to send parameters to Wavetable

## Example Prompts

- `warm airy neo soul pad`
- `dark trap bell`
- `nostalgic gospel keys`
- `ambient cinematic texture`
- `bright afro pluck`
- `deep house bass`
- `ethereal worship pad`
- `lo-fi hazy keys`

## Stopping the Engine

Double-click **`max_bridge/Stop_Engine.command`** — or just close the Terminal window.

## Troubleshooting

**"Engine not running" in the Max device**
→ Make sure you double-clicked `Start_Engine.command` first and the Terminal says "Engine is running!"

**"Python not found"**
→ Install Python 3.10+ from [python.org](https://www.python.org/downloads/)

**Port 8000 already in use**
→ Double-click `Stop_Engine.command` to kill the old process, then start again.

**Max device doesn't load the JS file**
→ Make sure `retrieve_and_apply.js` is in the same folder as the `.maxpat` or in Max's File Preferences search path.

## Requirements

- macOS 10.15+
- Python 3.10+
- Ableton Live 11+ with Max for Live
- No internet connection needed — everything runs locally
