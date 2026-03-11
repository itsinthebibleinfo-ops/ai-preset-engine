"""
Prompt-to-preset retrieval engine.

Deterministic scoring against the unified sound knowledge database.
Returns explainable results with score breakdown by:
  - family match
  - genre match
  - style cluster match
  - tag overlap
  - attribute alignment
  - provenance confidence

Usage:
    from sound_lab.scripts.retrieval_engine import RetrievalEngine

    engine = RetrievalEngine()
    results = engine.query("warm airy neo soul pad", top_k=5)
    print(json.dumps(results, indent=2))

CLI:
    python -m sound_lab.scripts.retrieval_engine "warm airy neo soul pad"
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

from sound_lab.scripts.tag_normalizer import TagNormalizer

logger = logging.getLogger(__name__)

# ── Paths ────────────────────────────────────────────────────────────────────────
import sys as _sys
if getattr(_sys, "frozen", False):
    _ROOT = Path(_sys._MEIPASS)
else:
    _ROOT = Path(__file__).resolve().parent.parent.parent       # ai-sound-design-engine/
KNOWLEDGE_PATH = _ROOT / "sound_lab" / "output" / "unified_sound_knowledge.json"

# ── Scoring weights ──────────────────────────────────────────────────────────────
W_FAMILY          = 4.0      # exact family match is highest priority
W_GENRE           = 3.0      # genre anchors the style
W_SUBGENRE        = 2.0      # subgenre refines further
W_STYLE_CLUSTER   = 3.5      # style cluster is a strong identity signal
W_TAG_EXACT       = 1.5      # each exact tag match
W_TAG_SYNONYM     = 1.0      # synonym-resolved tag match
W_ATTRIBUTE_ALIGN = 0.75     # attribute-name match
W_MOOD_MATCH      = 1.0      # mood alignment
W_PROVENANCE      = 0.5      # bonus for curated provenance

# ── Style cluster keyword index ──────────────────────────────────────────────────
# Used to boost presets whose style_cluster tokens overlap with query tokens.
def _cluster_tokens(cluster: str) -> set[str]:
    """Split a style_cluster like 'gospel_swell_pad' → {'gospel', 'swell', 'pad'}."""
    return set(cluster.lower().replace("-", "_").split("_"))


# ── Data classes ─────────────────────────────────────────────────────────────────

@dataclass
class ScoreBreakdown:
    """Explainable score components."""
    family: float = 0.0
    genre: float = 0.0
    subgenre: float = 0.0
    style_cluster: float = 0.0
    tag_overlap: float = 0.0
    attribute_alignment: float = 0.0
    mood: float = 0.0
    provenance: float = 0.0

    @property
    def total(self) -> float:
        return (self.family + self.genre + self.subgenre + self.style_cluster
                + self.tag_overlap + self.attribute_alignment + self.mood
                + self.provenance)


@dataclass
class ParsedPrompt:
    """Structured output of the prompt parser."""
    raw: str
    family: Optional[str] = None
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    moods: list[str] = field(default_factory=list)
    unknown_tokens: list[str] = field(default_factory=list)
    style_cluster_hints: list[str] = field(default_factory=list)


@dataclass
class RetrievalResult:
    """A single scored result with full breakdown."""
    rank: int
    preset_id: str
    preset_name: str
    family: str
    genre: str
    style_cluster: str
    tags: list[str]
    score: float
    breakdown: dict
    device_chain: list[str]
    attributes: dict
    parameters: dict


# ── Prompt Parser ────────────────────────────────────────────────────────────────

class PromptParser:
    """Parse natural-language prompts into structured queries using tag normalization."""

    # Bigrams that should be checked before individual tokens
    _BIGRAMS = [
        "neo soul", "hip hop", "lo fi", "sub bass", "deep house",
        "melodic house", "future bass", "electric piano", "uk drill",
        "synth pad", "synth lead", "old school", "afro beats",
    ]

    def __init__(self, normalizer: TagNormalizer) -> None:
        self._norm = normalizer

    def parse(self, prompt: str) -> ParsedPrompt:
        text = prompt.lower().strip()
        text = re.sub(r"[^\w\s\-&]", " ", text)

        result = ParsedPrompt(raw=prompt)
        consumed: set[int] = set()  # character positions consumed by bigrams

        # 1. Try bigram matches first
        tokens_from_bigrams: list[str] = []
        for bigram in self._BIGRAMS:
            if bigram in text:
                tokens_from_bigrams.append(bigram)
                # Mark positions as consumed
                idx = text.find(bigram)
                for i in range(idx, idx + len(bigram)):
                    consumed.add(i)

        # 2. Remaining single tokens — split by whitespace, skip consumed
        single_tokens = []
        for match in re.finditer(r"\S+", text):
            start, end = match.start(), match.end()
            # Skip if any character in this word was consumed by a bigram
            if any(i in consumed for i in range(start, end)):
                continue
            word = match.group().strip("-").strip()
            if word:
                single_tokens.append(word)

        all_tokens = tokens_from_bigrams + single_tokens

        # 3. Classify each token
        for token in all_tokens:
            info = self._norm.normalize_token(token)
            cat = info["category"]
            canon = info["canonical"]

            if cat == "genre":
                if result.genre is None:
                    result.genre = canon
                elif result.subgenre is None:
                    result.subgenre = canon
            elif cat == "family":
                if result.family is None:
                    result.family = canon
            elif cat == "tag":
                result.tags.append(canon)
            elif cat == "mood":
                result.moods.append(canon)
            else:
                # Unknown tokens still get added as tags for fuzzy matching
                result.tags.append(canon)
                result.unknown_tokens.append(token)

        # 4. Derive style cluster hints from all recognized tokens
        all_keywords = set()
        if result.family:
            all_keywords.add(result.family)
        if result.genre:
            all_keywords.add(result.genre)
        if result.subgenre:
            all_keywords.add(result.subgenre)
        all_keywords.update(result.tags)
        result.style_cluster_hints = sorted(all_keywords)

        return result


# ── Similarity Scorer ────────────────────────────────────────────────────────────

class SimilarityScorer:
    """Score a preset against a parsed prompt with full breakdown."""

    def __init__(self, normalizer: TagNormalizer) -> None:
        self._norm = normalizer

    def score(self, prompt: ParsedPrompt, preset: dict) -> ScoreBreakdown:
        bd = ScoreBreakdown()
        p_family = str(preset.get("family", "")).lower()
        p_genre = str(preset.get("genre", "")).lower()
        p_subgenre = str(preset.get("subgenre", "")).lower()
        p_cluster = str(preset.get("style_cluster", "")).lower()
        p_tags = {str(t).lower() for t in preset.get("tags", [])}
        p_attrs = preset.get("attributes", {})
        if not isinstance(p_attrs, dict):
            p_attrs = {}
        p_attr_keys = {k.lower() for k in p_attrs}

        # ── Family ───────────────────────────────────────────────────────────
        if prompt.family and prompt.family == p_family:
            bd.family = W_FAMILY

        # ── Genre ────────────────────────────────────────────────────────────
        if prompt.genre and prompt.genre == p_genre:
            bd.genre = W_GENRE
        elif prompt.genre and prompt.genre in p_subgenre:
            bd.genre = W_GENRE * 0.6

        # ── Subgenre ─────────────────────────────────────────────────────────
        if prompt.subgenre and prompt.subgenre == p_subgenre:
            bd.subgenre = W_SUBGENRE
        elif prompt.subgenre and prompt.subgenre in p_genre:
            bd.subgenre = W_SUBGENRE * 0.5

        # ── Style cluster ────────────────────────────────────────────────────
        cluster_tokens = _cluster_tokens(p_cluster) if p_cluster else set()
        hint_set = set(prompt.style_cluster_hints)
        overlap = len(cluster_tokens & hint_set)
        if overlap > 0:
            # Scale: more token overlap = stronger cluster match
            bd.style_cluster = min(W_STYLE_CLUSTER, overlap * (W_STYLE_CLUSTER / 3))

        # ── Tag overlap ──────────────────────────────────────────────────────
        exact_hits = 0
        synonym_hits = 0
        for qtag in prompt.tags:
            if qtag in p_tags:
                exact_hits += 1
            else:
                # Check if any preset tag is a synonym of the query tag
                for pt in p_tags:
                    canon_pt = self._norm.normalize_tag(pt)
                    if canon_pt and canon_pt == qtag:
                        synonym_hits += 1
                        break
        bd.tag_overlap = exact_hits * W_TAG_EXACT + synonym_hits * W_TAG_SYNONYM

        # ── Attribute alignment ──────────────────────────────────────────────
        for qtag in prompt.tags + prompt.moods:
            if qtag in p_attr_keys:
                bd.attribute_alignment += W_ATTRIBUTE_ALIGN

        # ── Mood ─────────────────────────────────────────────────────────────
        for mood in prompt.moods:
            # Check if mood concept is reflected in tags
            if mood in p_tags:
                bd.mood += W_MOOD_MATCH

        # ── Provenance ───────────────────────────────────────────────────────
        # Curated Ableton presets get a small baseline confidence bonus
        if preset.get("device_chain"):
            bd.provenance = W_PROVENANCE

        return bd


# ── Retrieval Engine ─────────────────────────────────────────────────────────────

class RetrievalEngine:
    """
    Top-level retrieval engine.

    Loads the unified knowledge, parses prompts, scores all presets,
    and returns ranked results with full breakdown.
    """

    def __init__(self, knowledge_path: Path | str | None = None) -> None:
        kp = Path(knowledge_path) if knowledge_path else KNOWLEDGE_PATH
        if not kp.exists():
            raise FileNotFoundError(
                f"Unified knowledge not found: {kp}. "
                "Run `python -m sound_lab.scripts.build_unified_knowledge` first."
            )
        with open(kp, "r", encoding="utf-8") as f:
            self._knowledge = json.load(f)

        self._presets: list[dict] = self._knowledge["presets"]
        self._vocabulary: dict = self._knowledge.get("vocabulary", {})
        self._normalizer = TagNormalizer()
        self._parser = PromptParser(self._normalizer)
        self._scorer = SimilarityScorer(self._normalizer)

        logger.info("RetrievalEngine loaded: %d presets", len(self._presets))

    @property
    def preset_count(self) -> int:
        return len(self._presets)

    @property
    def vocabulary(self) -> dict:
        return self._vocabulary

    def parse_prompt(self, prompt: str) -> ParsedPrompt:
        """Expose prompt parsing for inspection/debugging."""
        return self._parser.parse(prompt)

    def query(self, prompt: str, top_k: int = 5) -> dict:
        """
        Run a full retrieval query.

        Returns a JSON-serializable dict with:
          - query: the parsed prompt
          - results: top-k ranked presets with score breakdown
          - metadata: result count, max score, etc.
        """
        parsed = self._parser.parse(prompt)

        scored: list[tuple[float, ScoreBreakdown, dict]] = []
        for preset in self._presets:
            bd = self._scorer.score(parsed, preset)
            scored.append((bd.total, bd, preset))

        # Sort by total score descending, then by preset_id for determinism
        scored.sort(key=lambda x: (-x[0], x[2].get("preset_id", "")))

        top = scored[:top_k]

        results = []
        for rank, (total, bd, preset) in enumerate(top, 1):
            results.append(
                asdict(RetrievalResult(
                    rank=rank,
                    preset_id=preset.get("preset_id", ""),
                    preset_name=preset.get("preset_name", ""),
                    family=preset.get("family", ""),
                    genre=preset.get("genre", ""),
                    style_cluster=preset.get("style_cluster", ""),
                    tags=preset.get("tags", []),
                    score=round(total, 3),
                    breakdown={
                        "family": round(bd.family, 3),
                        "genre": round(bd.genre, 3),
                        "subgenre": round(bd.subgenre, 3),
                        "style_cluster": round(bd.style_cluster, 3),
                        "tag_overlap": round(bd.tag_overlap, 3),
                        "attribute_alignment": round(bd.attribute_alignment, 3),
                        "mood": round(bd.mood, 3),
                        "provenance": round(bd.provenance, 3),
                    },
                    device_chain=preset.get("device_chain", []),
                    attributes=preset.get("attributes", {}),
                    parameters=preset.get("parameters", {}),
                ))
            )

        return {
            "query": {
                "raw": parsed.raw,
                "parsed_family": parsed.family,
                "parsed_genre": parsed.genre,
                "parsed_subgenre": parsed.subgenre,
                "parsed_tags": parsed.tags,
                "parsed_moods": parsed.moods,
                "style_cluster_hints": parsed.style_cluster_hints,
                "unknown_tokens": parsed.unknown_tokens,
            },
            "results": results,
            "metadata": {
                "total_presets_searched": len(self._presets),
                "results_returned": len(results),
                "top_score": results[0]["score"] if results else 0,
            },
        }


# ── CLI ──────────────────────────────────────────────────────────────────────────

def main() -> None:
    import sys

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python -m sound_lab.scripts.retrieval_engine \"<prompt>\" [top_k]")
        print("\nExample prompts:")
        print('  "warm airy neo soul pad"')
        print('  "dark trap bell"')
        print('  "nostalgic gospel keys"')
        print('  "ambient cinematic texture"')
        print('  "deep house bass"')
        print('  "ethereal worship pad"')
        print('  "bouncy afrobeats pluck"')
        print('  "lo-fi hazy keys"')
        sys.exit(0)

    prompt = sys.argv[1]
    top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    engine = RetrievalEngine()
    result = engine.query(prompt, top_k=top_k)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
