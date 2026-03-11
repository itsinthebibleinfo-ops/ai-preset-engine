# AI Sound Design Engine

A preset recommendation engine for Ableton Live. Given a natural-language prompt describing a desired sound, the engine scores and retrieves the most relevant synthesizer presets.

## Project Structure

```
engine/          - Core logic (server, retriever, parser, similarity scoring)
taxonomy/        - Genre, sound family, and style cluster definitions
presets/         - Preset database (JSON)
tests/           - Pytest test suite
scripts/         - Utility scripts
data/            - Raw/processed data assets
models/          - ML models (future)
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the Server

```bash
uvicorn engine.server:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API

### `GET /`
Health check.

### `POST /generate`
Retrieve presets matching a prompt (v1 — simple scoring).

**Request body:**
```json
{
  "prompt": "warm dreamy pad for rnb",
  "top_k": 5
}
```

**Response:**
```json
{
  "prompt": "warm dreamy pad for rnb",
  "top_k": 5,
  "count": 5,
  "recommended_presets": [...]
}
```

### `POST /v2/generate`
Enhanced preset retrieval with explainable 8-dimensional scoring.

**Request body:**
```json
{
  "prompt": "warm airy neo soul pad",
  "top_k": 5
}
```

**Response:**
```json
{
  "query": {
    "raw": "warm airy neo soul pad",
    "parsed_family": "pad",
    "parsed_genre": "neo_soul",
    "parsed_tags": ["warm", "airy"],
    "parsed_moods": [],
    "style_cluster_hints": ["airy", "neo_soul", "pad", "warm"]
  },
  "results": [
    {
      "rank": 1,
      "preset_id": "pad_001",
      "preset_name": "Haze Haze",
      "family": "pad",
      "genre": "rnb",
      "score": 12.5,
      "breakdown": {
        "family": 4.0,
        "genre": 0.0,
        "subgenre": 2.0,
        "style_cluster": 2.333,
        "tag_overlap": 3.0,
        "attribute_alignment": 0.75,
        "mood": 0.0,
        "provenance": 0.5
      },
      "device_chain": ["Wavetable", "Chorus-Ensemble", "Hybrid Reverb"],
      "attributes": {"brightness": 0.26, "warmth": 0.62}
    }
  ],
  "metadata": {
    "total_presets_searched": 1000,
    "results_returned": 5,
    "top_score": 12.5
  }
}
```

**Score breakdown dimensions:**
- `family` — exact sound family match (pad, bass, lead, keys, etc.)
- `genre` — genre alignment (rnb, trap, gospel, ambient, etc.)
- `subgenre` — subgenre refinement (neo_soul, worship, drill, etc.)
- `style_cluster` — token overlap with style cluster identity
- `tag_overlap` — exact and synonym tag matches
- `attribute_alignment` — attribute key matching
- `mood` — mood/theme alignment
- `provenance` — curated source confidence bonus

## Run Tests

```bash
pytest tests/ -v
```
