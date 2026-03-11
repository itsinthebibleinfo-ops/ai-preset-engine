"""Load, normalise, and retrieve presets from the JSON database."""

from __future__ import annotations

import json
import logging

from engine.config import PRESETS_PATH
from engine.prompt_parser import parse_prompt
from engine.similarity import score_preset

logger = logging.getLogger(__name__)


# ── Loader ────────────────────────────────────────────────────────────────────

def load_presets() -> list[dict]:
    """Load and normalise all presets from the JSON database."""
    if not PRESETS_PATH.exists():
        raise FileNotFoundError(f"Presets file not found: {PRESETS_PATH}")

    try:
        with open(PRESETS_PATH, "r") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in presets file: {e}")

    if not isinstance(data, list):
        raise ValueError("presets.json must contain a JSON array of presets")

    if len(data) == 0:
        logger.warning("presets.json is empty — no presets to search")

    return [normalize_preset(p) for p in data]


# ── Normaliser ────────────────────────────────────────────────────────────────

def normalize_preset(preset: dict) -> dict:
    """
    Normalise multiple preset schemas into one common retrieval schema.

    Supports:
    - 1000-preset Ableton dataset schema (preset_id, preset_name, …)
    - Alternate schema (id, name, sound_family, character, macros, …)
    """
    attributes = preset.get("attributes")
    if attributes is None:
        attributes = preset.get("character", {})

    family = preset.get("family")
    if family is None:
        family = preset.get("sound_family", "")

    preset_name = preset.get("preset_name")
    if preset_name is None:
        preset_name = preset.get("name", "")

    preset_id = preset.get("preset_id")
    if preset_id is None:
        preset_id = preset.get("id", "")

    tags = preset.get("tags")
    if tags is None:
        tags = preset.get("macros", [])

    return {
        "preset_id": preset_id,
        "preset_name": preset_name,
        "genre": preset.get("genre", ""),
        "subgenre": preset.get("subgenre", ""),
        "family": family,
        "style_cluster": preset.get("style_cluster", ""),
        "tags": tags if isinstance(tags, list) else [],
        "attributes": attributes if isinstance(attributes, dict) else {},
        "device_chain": preset.get("device_chain", preset.get("recommended_fx_chain", [])),
        "parameters": preset.get("parameters", {}),
    }


# ── Retriever ─────────────────────────────────────────────────────────────────

def retrieve_presets(prompt: str, top_k: int = 5) -> list[dict]:
    """Score all presets against *prompt* and return the top-k matches."""
    presets = load_presets()
    query = parse_prompt(prompt)

    scored = []
    for preset in presets:
        score = score_preset(query, preset)
        scored.append((score, preset))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [preset for _score, preset in scored[:top_k]]
