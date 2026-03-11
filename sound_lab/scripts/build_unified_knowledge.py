"""
Build the unified sound knowledge database.

Merges:
  - 1000 Ableton presets (family, genre, tags, attributes, parameters)
  - Jamendo MTG vocabulary (genres, instruments, moods)
  - DX7 patch names (FM synthesis reference names)

Output: sound_lab/output/unified_sound_knowledge.json
"""

from __future__ import annotations

import json
import logging
import os
from collections import Counter
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent          # ai-sound-design-engine/
PRESETS_PATH = ROOT / "presets" / "presets.json"
JAMENDO_DIR = ROOT / "sound_lab" / "datasets" / "jamendo_meta"
DX7_JSON_DIR = Path.home() / "Desktop" / "sound_lab" / "datasets" / "sound_lab" / "datasets" / "dx7_json"
OUTPUT_PATH = ROOT / "sound_lab" / "output" / "unified_sound_knowledge.json"


# ── Helpers ──────────────────────────────────────────────────────────────────────

def _load_json(path: Path) -> list | dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_jamendo_tags(tsv_path: Path, prefix: str) -> set[str]:
    """Extract unique tags from a Jamendo TSV, stripping the given prefix."""
    tags: set[str] = set()
    if not tsv_path.exists():
        return tags
    with open(tsv_path, "r", encoding="utf-8") as f:
        next(f)  # skip header
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 6:
                continue
            for raw_tag in parts[5].split(","):
                raw_tag = raw_tag.strip()
                if raw_tag.startswith(prefix):
                    tags.add(raw_tag[len(prefix):])
    return tags


def _collect_dx7_names(dx7_dir: Path) -> list[str]:
    """Walk the DX7 JSON patch dirs and collect patch names."""
    names: list[str] = []
    if not dx7_dir.exists():
        logger.warning("DX7 dir not found: %s", dx7_dir)
        return names
    for dirpath, _, filenames in os.walk(dx7_dir):
        for fn in filenames:
            if not fn.endswith(".json") or fn == "package.json":
                continue
            try:
                with open(os.path.join(dirpath, fn), "r") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "name" in data:
                    names.append(data["name"].strip())
                elif isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and "name" in entry:
                            names.append(entry["name"].strip())
            except Exception:
                continue
    return sorted(set(names))


# ── Build ────────────────────────────────────────────────────────────────────────

def build() -> dict:
    """Assemble the unified sound knowledge database."""
    # 1. Ableton presets
    presets = _load_json(PRESETS_PATH)
    logger.info("Loaded %d Ableton presets", len(presets))

    # Derive preset vocabulary
    preset_genres = sorted({p.get("genre", "") for p in presets} - {""})
    preset_families = sorted({p.get("family", "") for p in presets} - {""})
    preset_style_clusters = sorted({p.get("style_cluster", "") for p in presets} - {""})
    preset_tags = sorted({t for p in presets for t in p.get("tags", [])})
    preset_subgenres = sorted({p.get("subgenre", "") for p in presets} - {""})

    # 2. Jamendo vocabulary
    jamendo_genres = sorted(_parse_jamendo_tags(JAMENDO_DIR / "autotagging_genre.tsv", "genre---"))
    jamendo_instruments = sorted(_parse_jamendo_tags(JAMENDO_DIR / "autotagging_instrument.tsv", "instrument---"))
    jamendo_moods = sorted(_parse_jamendo_tags(JAMENDO_DIR / "autotagging_moodtheme.tsv", "mood/theme---"))
    logger.info("Jamendo vocab: %d genres, %d instruments, %d moods",
                len(jamendo_genres), len(jamendo_instruments), len(jamendo_moods))

    # 3. DX7 patch names (FM synthesis reference)
    dx7_names = _collect_dx7_names(DX7_JSON_DIR)
    logger.info("DX7 patch names: %d", len(dx7_names))

    # 4. Family distribution
    family_dist = dict(Counter(p.get("family", "") for p in presets).most_common())

    # 5. Assemble unified knowledge
    knowledge = {
        "version": "1.0.0",
        "description": "Unified sound knowledge database for prompt-to-preset retrieval.",
        "sources": {
            "ableton_presets": {
                "count": len(presets),
                "provenance": "curated_ableton_library"
            },
            "jamendo_mtg": {
                "genres": len(jamendo_genres),
                "instruments": len(jamendo_instruments),
                "moods": len(jamendo_moods),
                "provenance": "mtg_jamendo_autotagging"
            },
            "dx7_patches": {
                "count": len(dx7_names),
                "provenance": "yamaha_dx7_community_patches"
            }
        },
        "vocabulary": {
            "genres": sorted(set(preset_genres) | set(jamendo_genres)),
            "families": preset_families,
            "style_clusters": preset_style_clusters,
            "subgenres": preset_subgenres,
            "tags": preset_tags,
            "instruments": jamendo_instruments,
            "moods": jamendo_moods,
        },
        "family_distribution": family_dist,
        "presets": presets,
        "dx7_reference_names": dx7_names,
    }
    return knowledge


def main() -> None:
    knowledge = build()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, indent=2, ensure_ascii=False)
    logger.info("Wrote unified knowledge to %s", OUTPUT_PATH)
    logger.info("  Presets: %d", len(knowledge["presets"]))
    logger.info("  Vocab genres: %d", len(knowledge["vocabulary"]["genres"]))
    logger.info("  Vocab tags: %d", len(knowledge["vocabulary"]["tags"]))
    logger.info("  DX7 names: %d", len(knowledge["dx7_reference_names"]))


if __name__ == "__main__":
    main()
