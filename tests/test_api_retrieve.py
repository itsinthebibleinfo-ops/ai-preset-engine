"""Tests for the /api/retrieve Max bridge endpoint."""

import pytest
from fastapi.testclient import TestClient

from engine.server import app


@pytest.fixture
def client():
    return TestClient(app)


# ── Contract stability tests ─────────────────────────────────────────────────

class TestRetrieveContract:
    def test_returns_200(self, client):
        resp = client.post(
            "/api/retrieve",
            json={"prompt": "warm airy neo soul pad", "top_k": 3},
        )
        assert resp.status_code == 200

    def test_top_level_shape(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "warm pad rnb", "top_k": 3},
        ).json()
        assert "prompt" in data
        assert "results" in data
        assert "warnings" in data
        assert isinstance(data["results"], list)
        assert isinstance(data["warnings"], list)

    def test_prompt_echoed(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "dark trap bell", "top_k": 1},
        ).json()
        assert data["prompt"] == "dark trap bell"

    def test_result_has_required_fields(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "warm airy neo soul pad", "top_k": 1},
        ).json()
        assert len(data["results"]) > 0
        r = data["results"][0]
        assert "preset_name" in r
        assert "family" in r
        assert "style_cluster" in r
        assert "device_chain" in r
        assert "parameters" in r
        assert "score" in r
        assert "score_breakdown" in r
        assert "provenance" in r

    def test_score_breakdown_has_5_dimensions(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "warm pad", "top_k": 1},
        ).json()
        bd = data["results"][0]["score_breakdown"]
        assert set(bd.keys()) == {
            "family", "style_cluster", "tag_overlap",
            "attributes", "provenance_confidence",
        }

    def test_provenance_shape(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "ambient texture", "top_k": 1},
        ).json()
        prov = data["results"][0]["provenance"]
        assert "source_dataset" in prov
        assert "confidence" in prov
        assert prov["source_dataset"] == "unified_sound_knowledge"


# ── Score normalization tests ─────────────────────────────────────────────────

class TestScoreNormalization:
    def test_scores_in_0_1_range(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "warm airy neo soul pad", "top_k": 5},
        ).json()
        for r in data["results"]:
            assert 0.0 <= r["score"] <= 1.0, f"Score out of range: {r['score']}"

    def test_breakdown_values_in_0_1_range(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "dark trap bell", "top_k": 3},
        ).json()
        for r in data["results"]:
            bd = r["score_breakdown"]
            for key, val in bd.items():
                assert 0.0 <= val <= 1.0, f"{key} out of range: {val}"

    def test_score_equals_breakdown_sum(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "gospel worship keys", "top_k": 1},
        ).json()
        r = data["results"][0]
        bd = r["score_breakdown"]
        expected = round(
            bd["family"] + bd["style_cluster"] + bd["tag_overlap"]
            + bd["attributes"] + bd["provenance_confidence"],
            3,
        )
        assert abs(r["score"] - expected) < 0.002


# ── Input validation tests ───────────────────────────────────────────────────

class TestRetrieveValidation:
    def test_empty_prompt_rejected(self, client):
        resp = client.post(
            "/api/retrieve",
            json={"prompt": "", "top_k": 3},
        )
        assert resp.status_code == 422

    def test_missing_prompt_rejected(self, client):
        resp = client.post(
            "/api/retrieve",
            json={"top_k": 3},
        )
        assert resp.status_code == 422

    def test_top_k_too_high_rejected(self, client):
        resp = client.post(
            "/api/retrieve",
            json={"prompt": "warm pad", "top_k": 99},
        )
        assert resp.status_code == 422

    def test_respects_top_k(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "warm pad", "top_k": 2},
        ).json()
        assert len(data["results"]) <= 2

    def test_default_top_k_is_3(self, client):
        data = client.post(
            "/api/retrieve",
            json={"prompt": "warm pad"},
        ).json()
        assert len(data["results"]) <= 3


# ── Multi-prompt smoke tests ─────────────────────────────────────────────────

class TestMultiPromptSmoke:
    """Test all 5 recommended prompts return valid results."""

    @pytest.mark.parametrize("prompt", [
        "warm airy neo soul pad",
        "dark trap bell",
        "nostalgic gospel keys",
        "ambient cinematic texture",
        "bright afro pluck",
    ])
    def test_prompt_returns_results(self, client, prompt):
        data = client.post(
            "/api/retrieve",
            json={"prompt": prompt, "top_k": 3},
        ).json()
        assert len(data["results"]) > 0
        assert data["prompt"] == prompt
        # Top result has a positive score
        assert data["results"][0]["score"] > 0


# ── Backward compatibility ────────────────────────────────────────────────────

class TestBackwardCompatibility:
    def test_v1_generate_still_works(self, client):
        resp = client.post(
            "/generate",
            json={"prompt": "warm pad rnb", "top_k": 3},
        )
        assert resp.status_code == 200
        assert "recommended_presets" in resp.json()

    def test_v2_generate_still_works(self, client):
        resp = client.post(
            "/v2/generate",
            json={"prompt": "warm pad rnb", "top_k": 3},
        )
        assert resp.status_code == 200
        assert "results" in resp.json()

    def test_health_check(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
