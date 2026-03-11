"""Shared pytest fixtures for the AI Sound Design Engine test suite."""

import pytest


# ── Sample presets ────────────────────────────────────────────────────────────

@pytest.fixture
def sample_rnb_pad():
    """A normalised R&B pad preset."""
    return {
        "preset_id": "pad_001",
        "preset_name": "Haze Haze",
        "genre": "rnb",
        "subgenre": "neo_soul",
        "family": "pad",
        "style_cluster": "contemporary_rnb_pad",
        "tags": ["warm", "airy", "wide", "lush"],
        "attributes": {"brightness": 0.26, "warmth": 0.62, "stereo_width": 0.8},
        "device_chain": ["Wavetable", "Chorus-Ensemble", "Hybrid Reverb"],
        "parameters": {},
    }


@pytest.fixture
def sample_trap_bass():
    """A normalised trap bass preset."""
    return {
        "preset_id": "bass_050",
        "preset_name": "808 Rumble",
        "genre": "hip_hop",
        "subgenre": "trap",
        "family": "bass",
        "style_cluster": "808_trap_bass",
        "tags": ["dark", "heavy", "sub", "808"],
        "attributes": {"warmth": 0.5, "brightness": 0.1, "weight": 0.95},
        "device_chain": ["Operator", "Saturator", "EQ Eight"],
        "parameters": {},
    }


@pytest.fixture
def sample_gospel_keys():
    """A normalised gospel keys preset."""
    return {
        "preset_id": "keys_010",
        "preset_name": "Sunday Morning Keys",
        "genre": "gospel",
        "subgenre": "worship",
        "family": "keys",
        "style_cluster": "gospel_bright_keys",
        "tags": ["warm", "bright", "electric_piano", "soulful"],
        "attributes": {"warmth": 0.85, "brightness": 0.5},
        "device_chain": ["Electric", "Chorus-Ensemble", "Reverb"],
        "parameters": {},
    }


@pytest.fixture
def sample_ambient_texture():
    """A normalised ambient texture preset."""
    return {
        "preset_id": "texture_020",
        "preset_name": "Stellar Dust",
        "genre": "ambient",
        "subgenre": "atmospheric",
        "family": "texture",
        "style_cluster": "ambient_texture",
        "tags": ["spacey", "ambient", "evolving", "granular"],
        "attributes": {"warmth": 0.4, "brightness": 0.6, "movement": 0.9},
        "device_chain": ["Granulator II", "Reverb", "Delay"],
        "parameters": {},
    }


# ── Sample queries ────────────────────────────────────────────────────────────

@pytest.fixture
def query_warm_pad():
    return {
        "family": "pad",
        "genre": None,
        "subgenre": None,
        "style_clusters": ["contemporary_rnb_pad"],
        "tags": ["warm", "pad"],
        "attributes": ["warm", "pad"],
    }


@pytest.fixture
def query_dark_trap_bass():
    return {
        "family": "bass",
        "genre": None,
        "subgenre": None,
        "style_clusters": ["trap_atmospheric_pad", "808_trap_bass"],
        "tags": ["dark", "trap", "bass"],
        "attributes": ["dark", "trap", "bass"],
    }


@pytest.fixture
def query_empty():
    return {
        "family": None,
        "genre": None,
        "subgenre": None,
        "style_clusters": [],
        "tags": [],
        "attributes": [],
    }


# ── Alternate-schema preset (for normaliser tests) ───────────────────────────

@pytest.fixture
def alt_schema_preset():
    """A preset using the alternate id/name/sound_family/character/macros schema."""
    return {
        "id": "alt_001",
        "name": "Alt Test",
        "genre": "trap",
        "sound_family": "bass",
        "character": {"weight": 0.9},
        "macros": ["macro1"],
    }
