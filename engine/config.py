"""Centralized configuration for the AI Sound Design Engine."""

import json
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle — data files live under sys._MEIPASS
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
PRESETS_PATH = BASE_DIR / "presets" / "presets.json"
TAXONOMY_DIR = BASE_DIR / "taxonomy"

# ── Sound Lab datasets ─────────────────────────────────────────────────────────
SOUND_LAB_DIR = BASE_DIR / "sound_lab"
JAMENDO_META_DIR = SOUND_LAB_DIR / "datasets" / "jamendo_meta"
NSYNTH_META_DIR = SOUND_LAB_DIR / "datasets" / "nsynth_meta"
DX7_META_DIR = SOUND_LAB_DIR / "datasets" / "dx7_meta"
ABLETON_PRESETS_DIR = SOUND_LAB_DIR / "datasets" / "ableton_presets"
SOUND_LAB_FEATURES_DIR = SOUND_LAB_DIR / "features"
SOUND_LAB_ARCHETYPES_DIR = SOUND_LAB_DIR / "archetypes"

# ── Scoring weights (used by similarity.py) ────────────────────────────────────
WEIGHT_FAMILY = 3.0
WEIGHT_GENRE = 2.0
WEIGHT_STYLE_CLUSTER = 3.0
WEIGHT_TAG = 1.5
WEIGHT_ATTRIBUTE = 1.0
WEIGHT_SUBGENRE = 1.5

# ── API defaults ───────────────────────────────────────────────────────────────
DEFAULT_TOP_K = 5
MAX_TOP_K = 50
MAX_PROMPT_LENGTH = 500


# ── Taxonomy loader ───────────────────────────────────────────────────────────
def _load_taxonomy_file(filename: str) -> list:
    """Load a taxonomy JSON array from the taxonomy directory."""
    path = TAXONOMY_DIR / filename
    if not path.exists():
        logger.warning("Taxonomy file not found: %s", path)
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list):
            logger.warning("Taxonomy file %s is not a JSON array", path)
            return []
        return data
    except json.JSONDecodeError:
        logger.warning("Invalid JSON in taxonomy file: %s", path)
        return []


def load_genres() -> list[str]:
    return _load_taxonomy_file("genres.json")


def load_sound_families() -> list[str]:
    return _load_taxonomy_file("sound_families.json")


def load_style_clusters() -> list[str]:
    return _load_taxonomy_file("style_clusters.json")
