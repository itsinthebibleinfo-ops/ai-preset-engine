"""
Loader for the MTG-Jamendo dataset TSV files.

Reads the autotagging TSVs, extracts unique tag vocabularies, and provides
query helpers that the engine can use for enrichment and validation.

Usage:
    from sound_lab.scripts.load_jamendo import JamendoLoader

    loader = JamendoLoader()            # auto-discovers TSVs
    loader.load()                       # parse everything
    print(loader.genres)                # {'rock', 'pop', ...}
    print(loader.instruments)           # {'guitar', 'piano', ...}
    print(loader.moods)                 # {'dark', 'happy', ...}
    tracks = loader.search_by_tags(['rock', 'guitar'])
"""

from __future__ import annotations

import csv
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Paths ───────────────────────────────────────────────────────────────────────
_BASE = Path(__file__).resolve().parent.parent          # sound_lab/
JAMENDO_DIR = _BASE / "datasets" / "jamendo_meta"
MANIFEST_PATH = JAMENDO_DIR / "manifest.json"

# Tag category prefixes used in MTG-Jamendo
_PREFIX_GENRE = "genre---"
_PREFIX_INSTRUMENT = "instrument---"
_PREFIX_MOOD = "mood/theme---"


# ── Data classes ────────────────────────────────────────────────────────────────
@dataclass
class JamendoTrack:
    """One row from a Jamendo TSV."""
    track_id: str
    artist_id: str
    album_id: str
    path: str
    duration: float
    tags: list[str] = field(default_factory=list)
    # Extra fields from raw.meta.tsv
    track_name: Optional[str] = None
    artist_name: Optional[str] = None
    album_name: Optional[str] = None
    release_date: Optional[str] = None
    url: Optional[str] = None


# ── Loader ──────────────────────────────────────────────────────────────────────
class JamendoLoader:
    """Loads and indexes the MTG-Jamendo metadata TSVs."""

    def __init__(self, data_dir: Path | str | None = None) -> None:
        self.data_dir = Path(data_dir) if data_dir else JAMENDO_DIR
        self.tracks: dict[str, JamendoTrack] = {}       # track_id → track
        self.tag_index: dict[str, set[str]] = defaultdict(set)  # tag → {track_ids}

        # Extracted vocabularies
        self.genres: set[str] = set()
        self.instruments: set[str] = set()
        self.moods: set[str] = set()
        self.all_tags: set[str] = set()

        self._loaded = False

    # ── Public API ──────────────────────────────────────────────────────────────

    def load(self) -> None:
        """Parse all core TSVs and build indexes."""
        if self._loaded:
            return

        self._load_tagged_tsv("autotagging_genre.tsv")
        self._load_tagged_tsv("autotagging_instrument.tsv")
        self._load_tagged_tsv("autotagging_moodtheme.tsv")
        self._load_tagged_tsv("autotagging_top50tags.tsv")
        self._load_tagged_tsv("raw_30s_cleantags.tsv")
        self._load_meta_tsv("raw.meta.tsv")

        self._loaded = True
        logger.info(
            "Jamendo loaded: %d tracks, %d genres, %d instruments, %d moods, %d total tags",
            len(self.tracks),
            len(self.genres),
            len(self.instruments),
            len(self.moods),
            len(self.all_tags),
        )

    def search_by_tags(self, tags: list[str], match_all: bool = False) -> list[JamendoTrack]:
        """Return tracks matching any (or all) of the given tags."""
        self._ensure_loaded()
        normalized = [t.lower().replace(" ", "") for t in tags]
        hit_sets = [self.tag_index.get(t, set()) for t in normalized]
        if match_all:
            result_ids = set.intersection(*hit_sets) if hit_sets else set()
        else:
            result_ids = set.union(*hit_sets) if hit_sets else set()
        return [self.tracks[tid] for tid in result_ids if tid in self.tracks]

    def get_track(self, track_id: str) -> Optional[JamendoTrack]:
        self._ensure_loaded()
        return self.tracks.get(track_id)

    def summary(self) -> dict:
        """Return a compact summary of the loaded dataset."""
        self._ensure_loaded()
        return {
            "total_tracks": len(self.tracks),
            "unique_genres": sorted(self.genres),
            "unique_instruments": sorted(self.instruments),
            "unique_moods": sorted(self.moods),
            "total_unique_tags": len(self.all_tags),
        }

    # ── Private helpers ─────────────────────────────────────────────────────────

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    def _load_tagged_tsv(self, filename: str) -> None:
        """Parse a TRACK_ID … TAGS tsv and index tags."""
        path = self.data_dir / filename
        if not path.exists():
            logger.warning("Jamendo TSV not found: %s", path)
            return

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                track_id = row.get("TRACK_ID", "").strip()
                if not track_id:
                    continue

                # Upsert track
                if track_id not in self.tracks:
                    self.tracks[track_id] = JamendoTrack(
                        track_id=track_id,
                        artist_id=row.get("ARTIST_ID", ""),
                        album_id=row.get("ALBUM_ID", ""),
                        path=row.get("PATH", ""),
                        duration=float(row.get("DURATION", 0) or 0),
                    )

                # Parse tags (comma-separated in TAGS column)
                raw_tags = row.get("TAGS", "")
                for raw in raw_tags.split(","):
                    raw = raw.strip()
                    if not raw:
                        continue

                    # Strip prefix and classify
                    if raw.startswith(_PREFIX_GENRE):
                        clean = raw[len(_PREFIX_GENRE):]
                        self.genres.add(clean)
                    elif raw.startswith(_PREFIX_INSTRUMENT):
                        clean = raw[len(_PREFIX_INSTRUMENT):]
                        self.instruments.add(clean)
                    elif raw.startswith(_PREFIX_MOOD):
                        clean = raw[len(_PREFIX_MOOD):]
                        self.moods.add(clean)
                    else:
                        clean = raw

                    normalized = clean.lower().replace(" ", "")
                    self.all_tags.add(clean)
                    self.tracks[track_id].tags.append(clean)
                    self.tag_index[normalized].add(track_id)

        logger.debug("Parsed %s", filename)

    def _load_meta_tsv(self, filename: str) -> None:
        """Enrich existing tracks with metadata from raw.meta.tsv."""
        path = self.data_dir / filename
        if not path.exists():
            logger.warning("Jamendo meta TSV not found: %s", path)
            return

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                track_id = row.get("TRACK_ID", "").strip()
                track = self.tracks.get(track_id)
                if track is None:
                    continue
                track.track_name = row.get("TRACK_NAME")
                track.artist_name = row.get("ARTIST_NAME")
                track.album_name = row.get("ALBUM_NAME")
                track.release_date = row.get("RELEASEDATE")
                track.url = row.get("URL")


# ── CLI convenience ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    loader = JamendoLoader()
    loader.load()
    summary = loader.summary()
    print(json.dumps(summary, indent=2))

    if len(sys.argv) > 1:
        query_tags = sys.argv[1:]
        hits = loader.search_by_tags(query_tags)
        print(f"\n{len(hits)} tracks matching {query_tags}")
        for t in hits[:10]:
            print(f"  {t.track_id}  {t.track_name or '(unnamed)'}  tags={t.tags[:5]}")
