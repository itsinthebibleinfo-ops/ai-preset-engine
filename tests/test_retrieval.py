"""Tests for the AI Sound Design Engine."""

import pytest

from engine.config import (
    PRESETS_PATH,
    WEIGHT_FAMILY,
    load_genres,
    load_sound_families,
    load_style_clusters,
)
from engine.models import GenerateRequest, NormalizedPreset, ParsedQuery
from engine.preset_generator import generate_preset
from engine.preset_retriever import load_presets, normalize_preset, retrieve_presets
from engine.prompt_parser import FAMILIES, GENRES, parse_prompt
from engine.similarity import score_preset


# ── Config tests ──────────────────────────────────────────────────────────────

class TestConfig:
    def test_presets_path_exists(self):
        assert PRESETS_PATH.exists()

    def test_load_genres_returns_list(self):
        genres = load_genres()
        assert isinstance(genres, list)
        assert len(genres) > 0

    def test_load_sound_families_returns_list(self):
        families = load_sound_families()
        assert isinstance(families, list)
        assert len(families) > 0

    def test_load_style_clusters_returns_list(self):
        clusters = load_style_clusters()
        assert isinstance(clusters, list)
        assert len(clusters) > 0


# ── Prompt parser tests ───────────────────────────────────────────────────────

class TestParsePrompt:
    def test_extracts_family(self):
        result = parse_prompt("warm pad")
        assert result["family"] == "pad"

    def test_extracts_genre(self):
        result = parse_prompt("dark rnb bass")
        assert result["genre"] == "rnb"

    def test_extracts_style_cluster(self):
        result = parse_prompt("warm lush")
        assert "contemporary_rnb_pad" in result["style_clusters"]

    def test_extracts_lofi_cluster(self):
        result = parse_prompt("lofi chill pad")
        assert "lofi_hazy_pad" in result["style_clusters"]
        assert "lofi_soft_keys" in result["style_clusters"]

    def test_extracts_subgenre(self):
        result = parse_prompt("worship pad")
        assert result["subgenre"] == "worship"

    def test_all_words_become_tags(self):
        result = parse_prompt("warm pad rnb")
        assert "warm" in result["tags"]
        assert "pad" in result["tags"]
        assert "rnb" in result["tags"]

    def test_empty_prompt(self):
        result = parse_prompt("")
        assert result["family"] is None
        assert result["genre"] is None
        assert result["style_clusters"] == []

    def test_case_insensitive(self):
        result = parse_prompt("WARM PAD RNB")
        assert result["family"] == "pad"
        assert result["genre"] == "rnb"

    def test_families_loaded_from_taxonomy(self):
        assert "pad" in FAMILIES
        assert "arp" in FAMILIES
        assert "fx" in FAMILIES

    def test_genres_loaded_from_taxonomy(self):
        assert "rnb" in GENRES
        assert "gospel" in GENRES
        assert "cinematic" in GENRES


# ── Similarity tests ──────────────────────────────────────────────────────────

class TestScorePreset:
    def test_family_match_scores_high(self, query_warm_pad, sample_rnb_pad):
        score = score_preset(query_warm_pad, sample_rnb_pad)
        assert score >= WEIGHT_FAMILY

    def test_genre_match_adds_score(self):
        query = {"family": None, "genre": "hip_hop", "subgenre": None, "style_clusters": [], "tags": [], "attributes": []}
        preset = {"family": "", "genre": "hip_hop", "subgenre": "", "style_cluster": "", "tags": [], "attributes": {}}
        score = score_preset(query, preset)
        assert score >= 2.0

    def test_style_cluster_match(self):
        query = {"family": None, "genre": None, "subgenre": None, "style_clusters": ["contemporary_rnb_pad"], "tags": [], "attributes": []}
        preset = {"family": "", "genre": "", "subgenre": "", "style_cluster": "contemporary_rnb_pad", "tags": [], "attributes": {}}
        score = score_preset(query, preset)
        assert score >= 3.0

    def test_subgenre_match(self):
        query = {"family": None, "genre": None, "subgenre": "worship", "style_clusters": [], "tags": [], "attributes": []}
        preset = {"family": "", "genre": "gospel", "subgenre": "worship", "style_cluster": "", "tags": [], "attributes": {}}
        score = score_preset(query, preset)
        assert score >= 1.5

    def test_no_match_scores_zero(self):
        query = {"family": "lead", "genre": "edm", "subgenre": None, "style_clusters": ["future_bass_lead"], "tags": [], "attributes": []}
        preset = {"family": "bass", "genre": "hip_hop", "subgenre": "trap", "style_cluster": "808_trap_bass", "tags": [], "attributes": {}}
        score = score_preset(query, preset)
        assert score == 0.0

    def test_tag_overlap_adds_score(self, sample_rnb_pad):
        query = {"family": None, "genre": None, "subgenre": None, "style_clusters": [], "tags": ["warm", "lush"], "attributes": []}
        score = score_preset(query, sample_rnb_pad)
        assert score >= 1.5


# ── Normaliser tests ──────────────────────────────────────────────────────────

class TestNormalizePreset:
    def test_normalizes_standard_schema(self):
        raw = {
            "preset_id": "p1",
            "preset_name": "Test",
            "genre": "rnb",
            "family": "pad",
            "tags": ["warm"],
            "attributes": {"warmth": 0.9},
        }
        result = normalize_preset(raw)
        assert result["preset_id"] == "p1"
        assert result["preset_name"] == "Test"
        assert result["family"] == "pad"
        assert "raw" not in result  # raw field removed in hardened version

    def test_normalizes_alternate_schema(self, alt_schema_preset):
        result = normalize_preset(alt_schema_preset)
        assert result["preset_id"] == "alt_001"
        assert result["preset_name"] == "Alt Test"
        assert result["family"] == "bass"
        assert result["tags"] == ["macro1"]
        assert result["attributes"] == {"weight": 0.9}


# ── Loader tests ──────────────────────────────────────────────────────────────

class TestLoadPresets:
    def test_loads_presets(self):
        presets = load_presets()
        assert len(presets) == 1000
        assert all("preset_id" in p for p in presets)

    def test_all_presets_have_required_fields(self):
        presets = load_presets()
        required = {"preset_id", "preset_name", "genre", "family", "tags", "attributes"}
        for p in presets:
            assert required.issubset(p.keys()), f"Missing fields in {p.get('preset_id')}"


# ── Retriever tests ───────────────────────────────────────────────────────────

class TestRetrievePresets:
    def test_returns_results_for_valid_prompt(self):
        results = retrieve_presets("warm pad rnb", top_k=3)
        assert 0 < len(results) <= 3

    def test_top_result_matches_family(self):
        results = retrieve_presets("heavy sub bass 808", top_k=3)
        assert len(results) > 0
        assert any(p["family"] == "bass" for p in results)

    def test_respects_top_k(self):
        results = retrieve_presets("ambient", top_k=2)
        assert len(results) <= 2

    def test_gospel_query_returns_gospel(self):
        results = retrieve_presets("gospel worship keys bright", top_k=3)
        assert any(p["genre"] == "gospel" for p in results)

    def test_afrobeats_query(self):
        results = retrieve_presets("afrobeats pluck bouncy", top_k=5)
        assert any(p["genre"] == "afrobeats" for p in results)


# ── Preset generator stub tests ───────────────────────────────────────────────

class TestPresetGenerator:
    def test_returns_dict(self):
        result = generate_preset("warm pad")
        assert isinstance(result, dict)
        assert result["_generated"] is True

    def test_passes_family_and_genre(self):
        result = generate_preset("test", family="pad", genre="rnb")
        assert result["family"] == "pad"
        assert result["genre"] == "rnb"


# ── Model validation tests ────────────────────────────────────────────────────

class TestModels:
    def test_generate_request_validates(self):
        req = GenerateRequest(prompt="warm pad", top_k=3)
        assert req.prompt == "warm pad"
        assert req.top_k == 3

    def test_generate_request_rejects_empty(self):
        with pytest.raises(Exception):
            GenerateRequest(prompt="", top_k=3)

    def test_generate_request_rejects_high_top_k(self):
        with pytest.raises(Exception):
            GenerateRequest(prompt="warm pad", top_k=100)

    def test_normalized_preset_model(self):
        p = NormalizedPreset(preset_id="test", family="pad")
        assert p.preset_id == "test"
        assert p.tags == []

    def test_parsed_query_model(self):
        q = ParsedQuery(family="pad", tags=["warm"])
        assert q.family == "pad"
        assert q.genre is None
