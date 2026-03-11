"""Parse natural-language prompts into structured queries."""

from __future__ import annotations

from engine.config import load_genres, load_sound_families


# ── Keyword → style-cluster mapping ───────────────────────────────────────────
# Maps descriptive words a user might type to the canonical style_cluster values
# present in the preset database.
STYLE_CLUSTER_MAP: dict[str, str] = {
    # R&B / neo-soul
    "warm": "contemporary_rnb_pad",
    "lush": "contemporary_rnb_pad",
    "neo-soul": "neo_soul_keys",
    "neo_soul": "neo_soul_keys",
    "soulful": "neo_soul_lead",
    # Gospel
    "heavenly": "gospel_swell_pad",
    "angelic": "worship_air_pad",
    "worship": "worship_air_pad",
    "churchy": "gospel_organ_lead",
    "gospel": "gospel_atmosphere",
    # Ambient / atmospheric
    "airy": "ambient_texture",
    "spacey": "ambient_texture",
    "ethereal": "ambient_texture",
    "vast": "ambient_texture",
    "atmospheric": "ambient_texture",
    "ambient": "ambient_texture",
    "evolving": "ambient_texture",
    # Trap / drill
    "dark": "trap_atmospheric_pad",
    "menacing": "trap_dark_bell_lead",
    "ominous": "drill_dark_pad",
    "cold": "drill_cold_keys",
    "eerie": "dark_drill_texture",
    "trap": "trap_atmospheric_pad",
    "drill": "drill_dark_pad",
    "808": "808_trap_bass",
    # Lo-fi
    "lofi": "lofi_hazy_pad",
    "lo-fi": "lofi_hazy_pad",
    "hazy": "lofi_hazy_pad",
    "dusty": "lofi_noise_texture",
    "vinyl": "lofi_noise_texture",
    "chill": "lofi_soft_keys",
    # House
    "deep": "house_deep_bass",
    "driving": "melodic_house_lead",
    "melodic": "melodic_house_lead",
    "hypnotic": "melodic_house_arp",
    # Afrobeats
    "afro": "afrobeats_pluck",
    "afrobeat": "afrobeats_lead",
    "afrobeats": "afrobeats_lead",
    "bouncy": "afrobeats_arp",
    "marimba": "afrobeats_marimba_keys",
    # Future bass / EDM
    "wobbly": "future_bass_wobble",
    "future": "future_bass_chord",
    "energetic": "future_bass_lead",
    # Cinematic
    "cinematic": "cinematic_braam",
    "dramatic": "cinematic_impact",
    "massive": "cinematic_braam",
    "impact": "cinematic_impact",
    # Vintage / retro
    "retro": "electric_piano_rnb",
    "vintage": "electric_piano_rnb",
    # Bright / pop
    "bright": "gospel_bright_keys",
    "shimmery": "ambient_shimmer_pluck",
    "sparkly": "rnb_glass_arp",
    "glass": "rnb_glass_arp",
    # FX / transitions
    "glitchy": "glitch_stutter",
    "riser": "riser_swell",
    "swell": "riser_swell",
}

# ── Load canonical families & genres from taxonomy at import time ─────────────
_loaded_families = {f.lower() for f in load_sound_families()}
FAMILIES: set[str] = _loaded_families or {
    "pad", "bass", "lead", "pluck", "keys", "texture", "drone", "arp", "fx",
}

_loaded_genres = {g.lower() for g in load_genres()}
GENRES: set[str] = _loaded_genres or {
    "rnb", "trap", "lofi", "ambient", "house", "afrobeats", "gospel",
    "hip_hop", "edm", "future_bass", "cinematic",
}

# Subgenre keywords that can appear in a prompt
SUBGENRES: set[str] = {
    "neo_soul", "neo-soul", "worship", "drill", "trap", "deep_house",
    "melodic_house", "lofi_hiphop", "afrobeat", "afrobeats_pop",
    "contemporary_rnb", "ambient_rnb", "gospel_soul", "gospel_pop",
    "glitch", "foley", "scoring", "trailer", "orchestral",
}


def parse_prompt(prompt: str) -> dict:
    """Parse a natural-language sound prompt into a structured query dict."""
    words = prompt.lower().split()

    family: str | None = None
    genre: str | None = None
    subgenre: str | None = None
    style_clusters: set[str] = set()
    tags: set[str] = set()
    attributes: set[str] = set()

    for word in words:
        if word in FAMILIES:
            family = word
        elif word in GENRES:
            genre = word
        elif word in SUBGENRES and subgenre is None:
            subgenre = word
        if word in STYLE_CLUSTER_MAP:
            style_clusters.add(STYLE_CLUSTER_MAP[word])
        tags.add(word)
        attributes.add(word)

    return {
        "family": family,
        "genre": genre,
        "subgenre": subgenre,
        "style_clusters": list(style_clusters),
        "tags": list(tags),
        "attributes": list(attributes),
    }
