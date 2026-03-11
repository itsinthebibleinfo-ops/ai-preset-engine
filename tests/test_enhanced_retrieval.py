"""Tests for the enhanced retrieval engine and /v2/generate endpoint."""

import pytest
from fastapi.testclient import TestClient

from sound_lab.scripts.retrieval_engine import PromptParser, RetrievalEngine, SimilarityScorer
from sound_lab.scripts.tag_normalizer import TagNormalizer
from engine.server import app


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    """Module-scoped engine to avoid reloading 1000 presets per test."""
    return RetrievalEngine()


@pytest.fixture
def parser():
    return PromptParser(TagNormalizer())


@pytest.fixture
def scorer():
    return SimilarityScorer(TagNormalizer())


@pytest.fixture
def client():
    return TestClient(app)


# ── RetrievalEngine tests ────────────────────────────────────────────────────

class TestRetrievalEngine:
    def test_engine_loads_presets(self, engine):
        assert engine.preset_count == 1000

    def test_engine_has_vocabulary(self, engine):
        vocab = engine.vocabulary
        assert "genres" in vocab
        assert "families" in vocab
        assert len(vocab["genres"]) > 0

    def test_query_returns_results(self, engine):
        result = engine.query("warm pad rnb", top_k=3)
        assert "query" in result
        assert "results" in result
        assert "metadata" in result
        assert len(result["results"]) <= 3

    def test_query_results_have_breakdown(self, engine):
        result = engine.query("dark trap bell", top_k=1)
        if result["results"]:
            r = result["results"][0]
            bd = r["breakdown"]
            assert set(bd.keys()) == {
                "family", "genre", "subgenre", "style_cluster",
                "tag_overlap", "attribute_alignment", "mood", "provenance",
            }

    def test_results_are_ranked_descending(self, engine):
        result = engine.query("warm airy neo soul pad", top_k=5)
        scores = [r["score"] for r in result["results"]]
        assert scores == sorted(scores, reverse=True)

    def test_metadata_counts(self, engine):
        result = engine.query("ambient cinematic texture", top_k=3)
        meta = result["metadata"]
        assert meta["total_presets_searched"] == 1000
        assert meta["results_returned"] <= 3

    def test_pad_family_query_returns_pads(self, engine):
        result = engine.query("warm lush pad", top_k=5)
        families = [r["family"] for r in result["results"]]
        assert "pad" in families

    def test_gospel_query_returns_gospel(self, engine):
        result = engine.query("gospel worship keys", top_k=5)
        genres = [r["genre"] for r in result["results"]]
        assert "gospel" in genres


# ── PromptParser tests ───────────────────────────────────────────────────────

class TestPromptParser:
    def test_parses_family(self, parser):
        parsed = parser.parse("warm pad")
        assert parsed.family == "pad"

    def test_parses_genre(self, parser):
        parsed = parser.parse("dark trap bell")
        assert parsed.genre == "trap"

    def test_bigram_neo_soul(self, parser):
        parsed = parser.parse("warm airy neo soul pad")
        assert parsed.genre == "neo_soul"

    def test_tags_extracted(self, parser):
        parsed = parser.parse("warm airy pad")
        assert "warm" in parsed.tags
        assert "airy" in parsed.tags

    def test_moods_extracted(self, parser):
        parsed = parser.parse("chill relaxed pad")
        assert len(parsed.moods) > 0

    def test_empty_prompt(self, parser):
        parsed = parser.parse("")
        assert parsed.family is None
        assert parsed.genre is None
        assert parsed.tags == []

    def test_style_cluster_hints(self, parser):
        parsed = parser.parse("warm pad trap")
        assert len(parsed.style_cluster_hints) > 0


# ── SimilarityScorer tests ───────────────────────────────────────────────────

class TestSimilarityScorer:
    def test_family_match_scores(self, parser, scorer):
        parsed = parser.parse("warm pad")
        preset = {"family": "pad", "genre": "", "subgenre": "", "style_cluster": "",
                  "tags": [], "attributes": {}, "device_chain": []}
        bd = scorer.score(parsed, preset)
        assert bd.family > 0

    def test_no_match_scores_zero(self, parser, scorer):
        parsed = parser.parse("warm pad")
        preset = {"family": "bass", "genre": "hip_hop", "subgenre": "trap",
                  "style_cluster": "808_trap_bass", "tags": ["heavy", "sub"],
                  "attributes": {}, "device_chain": []}
        bd = scorer.score(parsed, preset)
        assert bd.family == 0
        assert bd.genre == 0

    def test_provenance_bonus(self, parser, scorer):
        parsed = parser.parse("warm pad")
        preset_with = {"family": "pad", "genre": "", "subgenre": "", "style_cluster": "",
                       "tags": [], "attributes": {}, "device_chain": ["Wavetable"]}
        preset_without = {"family": "pad", "genre": "", "subgenre": "", "style_cluster": "",
                          "tags": [], "attributes": {}}
        bd_with = scorer.score(parsed, preset_with)
        bd_without = scorer.score(parsed, preset_without)
        assert bd_with.provenance > bd_without.provenance


# ── /v2/generate API tests ───────────────────────────────────────────────────

class TestV2GenerateEndpoint:
    def test_v2_returns_200(self, client):
        resp = client.post("/v2/generate", json={"prompt": "warm pad rnb", "top_k": 3})
        assert resp.status_code == 200

    def test_v2_response_shape(self, client):
        resp = client.post("/v2/generate", json={"prompt": "warm pad rnb", "top_k": 3})
        data = resp.json()
        assert "query" in data
        assert "results" in data
        assert "metadata" in data

    def test_v2_query_has_parsed_fields(self, client):
        resp = client.post("/v2/generate", json={"prompt": "warm pad rnb"})
        q = resp.json()["query"]
        assert q["raw"] == "warm pad rnb"
        assert "parsed_family" in q
        assert "parsed_genre" in q
        assert "parsed_tags" in q

    def test_v2_results_have_breakdowns(self, client):
        resp = client.post("/v2/generate", json={"prompt": "dark trap bell", "top_k": 1})
        results = resp.json()["results"]
        if results:
            assert "breakdown" in results[0]
            assert "score" in results[0]
            bd = results[0]["breakdown"]
            assert "family" in bd
            assert "genre" in bd
            assert "mood" in bd

    def test_v2_respects_top_k(self, client):
        resp = client.post("/v2/generate", json={"prompt": "ambient texture", "top_k": 2})
        assert len(resp.json()["results"]) <= 2

    def test_v2_metadata(self, client):
        resp = client.post("/v2/generate", json={"prompt": "gospel keys", "top_k": 5})
        meta = resp.json()["metadata"]
        assert meta["total_presets_searched"] == 1000
        assert meta["results_returned"] <= 5

    def test_v2_rejects_empty_prompt(self, client):
        resp = client.post("/v2/generate", json={"prompt": "", "top_k": 3})
        assert resp.status_code == 422

    def test_v1_still_works(self, client):
        """Backward compatibility: v1 /generate still works."""
        resp = client.post("/generate", json={"prompt": "warm pad rnb", "top_k": 3})
        assert resp.status_code == 200
        assert "recommended_presets" in resp.json()
