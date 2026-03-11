"""
Tag normalizer for the sound design retrieval engine.

Resolves synonyms, abbreviations, and natural-language descriptors
into canonical tag/genre/family forms used in the knowledge base.
Deterministic — no ML, no embeddings.
"""

from __future__ import annotations


# ── Synonym tables ───────────────────────────────────────────────────────────────
# Each maps user-typed variants → the canonical form in our knowledge base.

GENRE_SYNONYMS: dict[str, str] = {
    # R&B
    "r&b": "rnb", "r-and-b": "rnb", "randb": "rnb", "rhythm and blues": "rnb",
    "rnb": "rnb",
    # Hip-hop
    "hiphop": "hip_hop", "hip-hop": "hip_hop", "hip hop": "hip_hop",
    "rap": "hip_hop",
    # Neo-soul
    "neosoul": "neo_soul", "neo-soul": "neo_soul", "neo soul": "neo_soul",
    # Lo-fi
    "lo-fi": "lofi", "lo fi": "lofi", "lofi": "lofi",
    # Trap
    "trap": "trap",
    # Gospel
    "gospel": "gospel", "churchy": "gospel", "church": "gospel",
    # Worship
    "worship": "worship", "praise": "worship",
    # Afrobeats
    "afrobeats": "afrobeats", "afrobeat": "afrobeats", "afro": "afrobeats",
    "afro-beats": "afrobeats",
    # Ambient
    "ambient": "ambient", "atmospheric": "ambient",
    # Cinematic
    "cinematic": "cinematic", "filmscore": "cinematic", "film": "cinematic",
    "orchestral": "cinematic", "trailer": "cinematic", "score": "cinematic",
    # House
    "house": "house", "deephouse": "house", "deep house": "house",
    "melodic house": "house", "melodichouse": "house",
    # Pop
    "pop": "pop",
    # EDM
    "edm": "edm", "electronic": "edm",
    # Future bass
    "future bass": "future_bass", "futurebass": "future_bass",
    # Drill
    "drill": "drill", "uk drill": "drill",
}

FAMILY_SYNONYMS: dict[str, str] = {
    "pad": "pad", "pads": "pad", "synth pad": "pad",
    "bass": "bass", "sub": "bass", "808": "bass", "sub bass": "bass",
    "lead": "lead", "leads": "lead", "synth lead": "lead",
    "keys": "keys", "piano": "keys", "keyboard": "keys", "rhodes": "keys",
    "electric piano": "keys", "ep": "keys", "organ": "keys",
    "pluck": "pluck", "plucks": "pluck",
    "arp": "arp", "arps": "arp", "arpeggio": "arp",
    "texture": "texture", "textures": "texture",
    "fx": "fx", "sfx": "fx", "effect": "fx", "effects": "fx",
    "drone": "drone", "drones": "drone",
    "bell": "lead",  # bells typically live in lead family
    "string": "pad", "strings": "pad",
    "brass": "lead",
    "choir": "pad",
    "marimba": "keys",
    "guitar": "pluck",
}

TAG_SYNONYMS: dict[str, str] = {
    # Warmth spectrum
    "warm": "warm", "warmth": "warm", "cozy": "warm", "toasty": "warm",
    # Cold spectrum
    "cold": "cold", "icy": "cold", "frozen": "cold", "frigid": "cold",
    # Brightness
    "bright": "bright", "brilliant": "bright", "shiny": "bright",
    "sparkly": "bright", "crispy": "bright",
    # Dark
    "dark": "dark", "moody": "dark", "noir": "dark", "shadowy": "dark",
    "brooding": "dark", "sinister": "dark", "menacing": "dark",
    # Space / width
    "wide": "wide", "spacious": "wide", "expansive": "wide",
    "stereo": "wide", "vast": "wide",
    # Air
    "airy": "airy", "breathy": "airy", "open": "airy", "light": "airy",
    # Lush
    "lush": "lush", "thick": "lush", "rich": "lush", "full": "lush",
    # Ethereal
    "ethereal": "ethereal", "heavenly": "ethereal", "angelic": "ethereal",
    "celestial": "ethereal", "divine": "ethereal",
    # Gritty
    "gritty": "gritty", "dirty": "gritty", "raw": "gritty", "crunchy": "gritty",
    "distorted": "gritty",
    # Smooth
    "smooth": "smooth", "silky": "smooth", "creamy": "smooth", "buttery": "smooth",
    # Aggressive
    "aggressive": "aggressive", "hard": "aggressive", "harsh": "aggressive",
    "punchy": "aggressive",
    # Soft
    "soft": "soft", "gentle": "soft", "delicate": "soft", "subtle": "soft",
    # Nostalgic
    "nostalgic": "nostalgic", "retro": "nostalgic", "vintage": "nostalgic",
    "old school": "nostalgic", "oldschool": "nostalgic", "throwback": "nostalgic",
    # Evolving / motion
    "evolving": "evolving", "moving": "evolving", "shifting": "evolving",
    "morphing": "evolving", "animated": "evolving",
    # Deep
    "deep": "deep", "subby": "deep", "rumbling": "deep",
    # Eerie
    "eerie": "eerie", "spooky": "eerie", "haunting": "eerie", "ominous": "eerie",
    "creepy": "eerie",
    # Dreamy
    "dreamy": "dreamy", "hazy": "dreamy", "foggy": "dreamy",
    "misty": "dreamy", "floaty": "dreamy",
    # Textured
    "textured": "textured", "grainy": "textured", "dusty": "textured",
    "vinyl": "textured", "lofi": "textured",
}

MOOD_SYNONYMS: dict[str, str] = {
    "happy": "happy", "joyful": "happy", "uplifting": "uplifting",
    "energetic": "energetic", "hype": "energetic", "bouncy": "energetic",
    "chill": "calm", "relaxed": "calm", "calm": "calm", "peaceful": "calm",
    "melancholic": "melancholic", "sad": "melancholic", "somber": "melancholic",
    "dramatic": "dramatic", "epic": "epic", "powerful": "powerful",
    "emotional": "emotional", "passionate": "emotional",
    "mysterious": "dark", "suspenseful": "dark",
}


# ── Normalizer class ─────────────────────────────────────────────────────────────

class TagNormalizer:
    """Deterministic tag normalizer using synonym lookup tables."""

    def __init__(self) -> None:
        self._genre_map = GENRE_SYNONYMS
        self._family_map = FAMILY_SYNONYMS
        self._tag_map = TAG_SYNONYMS
        self._mood_map = MOOD_SYNONYMS

    def normalize_genre(self, token: str) -> str | None:
        """Return canonical genre or None if not recognized."""
        return self._genre_map.get(token.lower().strip())

    def normalize_family(self, token: str) -> str | None:
        """Return canonical family or None if not recognized."""
        return self._family_map.get(token.lower().strip())

    def normalize_tag(self, token: str) -> str | None:
        """Return canonical tag or None if not recognized."""
        return self._tag_map.get(token.lower().strip())

    def normalize_mood(self, token: str) -> str | None:
        """Return canonical mood or None if not recognized."""
        return self._mood_map.get(token.lower().strip())

    def normalize_token(self, token: str) -> dict:
        """
        Classify and normalize a single token.

        Returns dict with keys: original, canonical, category (genre|family|tag|mood|unknown).
        """
        t = token.lower().strip()
        if g := self._genre_map.get(t):
            return {"original": token, "canonical": g, "category": "genre"}
        if f := self._family_map.get(t):
            return {"original": token, "canonical": f, "category": "family"}
        if tag := self._tag_map.get(t):
            return {"original": token, "canonical": tag, "category": "tag"}
        if m := self._mood_map.get(t):
            return {"original": token, "canonical": m, "category": "mood"}
        return {"original": token, "canonical": t, "category": "unknown"}

    def normalize_prompt_tokens(self, tokens: list[str]) -> list[dict]:
        """Normalize a list of tokens from a parsed prompt."""
        return [self.normalize_token(t) for t in tokens]
