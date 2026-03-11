"""AI Sound Design Engine — preset retrieval and generation for Ableton Live."""

from engine.config import (
    BASE_DIR,
    PRESETS_PATH,
    TAXONOMY_DIR,
    load_genres,
    load_sound_families,
    load_style_clusters,
)
from engine.models import (
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    NormalizedPreset,
    ParsedQuery,
)
from engine.preset_retriever import load_presets, normalize_preset, retrieve_presets
from engine.prompt_parser import parse_prompt
from engine.similarity import score_preset

__all__ = [
    # config
    "BASE_DIR",
    "PRESETS_PATH",
    "TAXONOMY_DIR",
    "load_genres",
    "load_sound_families",
    "load_style_clusters",
    # models
    "GenerateRequest",
    "GenerateResponse",
    "HealthResponse",
    "NormalizedPreset",
    "ParsedQuery",
    # core
    "load_presets",
    "normalize_preset",
    "retrieve_presets",
    "parse_prompt",
    "score_preset",
]