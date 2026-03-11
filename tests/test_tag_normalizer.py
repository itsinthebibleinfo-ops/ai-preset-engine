"""Tests for the tag normalizer module."""

import pytest

from sound_lab.scripts.tag_normalizer import TagNormalizer


@pytest.fixture
def normalizer():
    return TagNormalizer()


# ── Genre normalization ──────────────────────────────────────────────────────

class TestGenreNormalization:
    def test_canonical_genre(self, normalizer):
        assert normalizer.normalize_genre("trap") == "trap"

    def test_synonym_resolves(self, normalizer):
        assert normalizer.normalize_genre("hiphop") == "hip_hop"
        assert normalizer.normalize_genre("hip-hop") == "hip_hop"
        assert normalizer.normalize_genre("rap") == "hip_hop"

    def test_neo_soul_variants(self, normalizer):
        assert normalizer.normalize_genre("neosoul") == "neo_soul"
        assert normalizer.normalize_genre("neo-soul") == "neo_soul"
        assert normalizer.normalize_genre("neo soul") == "neo_soul"

    def test_case_insensitive(self, normalizer):
        assert normalizer.normalize_genre("TRAP") == "trap"
        assert normalizer.normalize_genre("Gospel") == "gospel"

    def test_unknown_genre_returns_none(self, normalizer):
        assert normalizer.normalize_genre("metalcore") is None
        assert normalizer.normalize_genre("zydeco") is None


# ── Family normalization ─────────────────────────────────────────────────────

class TestFamilyNormalization:
    def test_canonical_family(self, normalizer):
        assert normalizer.normalize_family("pad") == "pad"
        assert normalizer.normalize_family("bass") == "bass"

    def test_plural_resolves(self, normalizer):
        assert normalizer.normalize_family("pads") == "pad"
        assert normalizer.normalize_family("leads") == "lead"

    def test_instrument_to_family(self, normalizer):
        assert normalizer.normalize_family("piano") == "keys"
        assert normalizer.normalize_family("rhodes") == "keys"
        assert normalizer.normalize_family("808") == "bass"

    def test_bell_maps_to_lead(self, normalizer):
        assert normalizer.normalize_family("bell") == "lead"

    def test_unknown_family_returns_none(self, normalizer):
        assert normalizer.normalize_family("xylophone") is None


# ── Tag normalization ────────────────────────────────────────────────────────

class TestTagNormalization:
    def test_canonical_tag(self, normalizer):
        assert normalizer.normalize_tag("warm") == "warm"
        assert normalizer.normalize_tag("dark") == "dark"

    def test_synonyms_resolve(self, normalizer):
        assert normalizer.normalize_tag("cozy") == "warm"
        assert normalizer.normalize_tag("toasty") == "warm"
        assert normalizer.normalize_tag("icy") == "cold"

    def test_brightness_synonyms(self, normalizer):
        assert normalizer.normalize_tag("brilliant") == "bright"
        assert normalizer.normalize_tag("sparkly") == "bright"

    def test_unknown_tag_returns_none(self, normalizer):
        assert normalizer.normalize_tag("spaghetti") is None


# ── Mood normalization ───────────────────────────────────────────────────────

class TestMoodNormalization:
    def test_canonical_mood(self, normalizer):
        assert normalizer.normalize_mood("calm") == "calm"

    def test_synonyms_resolve(self, normalizer):
        assert normalizer.normalize_mood("chill") == "calm"
        assert normalizer.normalize_mood("relaxed") == "calm"
        assert normalizer.normalize_mood("joyful") == "happy"
        assert normalizer.normalize_mood("hype") == "energetic"

    def test_unknown_mood_returns_none(self, normalizer):
        assert normalizer.normalize_mood("flummoxed") is None


# ── Token classification ─────────────────────────────────────────────────────

class TestNormalizeToken:
    def test_genre_token(self, normalizer):
        info = normalizer.normalize_token("trap")
        assert info["category"] == "genre"
        assert info["canonical"] == "trap"

    def test_family_token(self, normalizer):
        info = normalizer.normalize_token("pad")
        assert info["category"] == "family"
        assert info["canonical"] == "pad"

    def test_tag_token(self, normalizer):
        info = normalizer.normalize_token("warm")
        assert info["category"] == "tag"
        assert info["canonical"] == "warm"

    def test_mood_token(self, normalizer):
        info = normalizer.normalize_token("chill")
        assert info["category"] == "mood"
        assert info["canonical"] == "calm"

    def test_unknown_token(self, normalizer):
        info = normalizer.normalize_token("xyzzy")
        assert info["category"] == "unknown"
        assert info["canonical"] == "xyzzy"

    def test_preserves_original(self, normalizer):
        info = normalizer.normalize_token("HipHop")
        assert info["original"] == "HipHop"


# ── Batch normalization ──────────────────────────────────────────────────────

class TestBatchNormalization:
    def test_batch_returns_list(self, normalizer):
        results = normalizer.normalize_prompt_tokens(["warm", "pad", "trap"])
        assert len(results) == 3

    def test_batch_categories(self, normalizer):
        results = normalizer.normalize_prompt_tokens(["warm", "pad", "trap", "flurb"])
        cats = [r["category"] for r in results]
        assert cats == ["tag", "family", "genre", "unknown"]

    def test_empty_batch(self, normalizer):
        assert normalizer.normalize_prompt_tokens([]) == []
