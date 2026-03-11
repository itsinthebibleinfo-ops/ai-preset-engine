"""Retrieval API transform layer.

Bridges the internal RetrievalEngine (8-dimension weighted scoring) to the
Max-friendly /api/retrieve contract (5-dimension normalized 0-1 scoring).

Score normalization:
    raw_total / SCORE_CEILING, capped at 1.0

5-dimension mapping from the engine's 8 dimensions:
    family            ← family
    style_cluster     ← style_cluster
    tag_overlap       ← genre + subgenre + tag_overlap + mood
    attributes        ← attribute_alignment
    provenance_confidence ← provenance
"""

from __future__ import annotations

import logging
from pathlib import Path

from engine.query_models import (
    RetrieveProvenance,
    RetrieveResponse,
    RetrieveResult,
    RetrieveScoreBreakdown,
)

logger = logging.getLogger(__name__)

# The theoretical ceiling for normalizing raw weighted scores to 0-1.
# Derived from: W_FAMILY(4) + W_GENRE(3) + W_SUBGENRE(2) + W_STYLE_CLUSTER(3.5)
#               + ~2 tags(3.0) + W_ATTRIBUTE(0.75) + W_MOOD(1.0) + W_PROVENANCE(0.5)
# ≈ 17.75, rounded to 16.0 for a generous but realistic ceiling.
SCORE_CEILING = 16.0

_engine = None


def _get_engine():
    """Lazy singleton for the RetrievalEngine."""
    global _engine
    if _engine is None:
        from sound_lab.scripts.retrieval_engine import RetrievalEngine
        _engine = RetrievalEngine()
    return _engine


def _normalize(raw: float) -> float:
    """Normalize a raw score component to 0-1, capped at 1.0."""
    return round(min(raw / SCORE_CEILING, 1.0), 3)


def _build_breakdown(bd: dict) -> RetrieveScoreBreakdown:
    """Map 8-dimension raw breakdown → 5-dimension normalized breakdown."""
    raw_family = bd.get("family", 0.0)
    raw_style = bd.get("style_cluster", 0.0)
    raw_tag = (
        bd.get("genre", 0.0)
        + bd.get("subgenre", 0.0)
        + bd.get("tag_overlap", 0.0)
        + bd.get("mood", 0.0)
    )
    raw_attr = bd.get("attribute_alignment", 0.0)
    raw_prov = bd.get("provenance", 0.0)

    return RetrieveScoreBreakdown(
        family=_normalize(raw_family),
        style_cluster=_normalize(raw_style),
        tag_overlap=_normalize(raw_tag),
        attributes=_normalize(raw_attr),
        provenance_confidence=_normalize(raw_prov),
    )


def _build_result(raw_result: dict) -> RetrieveResult:
    """Transform a single engine result into the Max-friendly contract."""
    bd = raw_result.get("breakdown", {})
    breakdown = _build_breakdown(bd)

    # Total normalized score = sum of breakdown dimensions
    total = round(
        breakdown.family
        + breakdown.style_cluster
        + breakdown.tag_overlap
        + breakdown.attributes
        + breakdown.provenance_confidence,
        3,
    )

    return RetrieveResult(
        preset_name=raw_result.get("preset_name", ""),
        family=raw_result.get("family", ""),
        style_cluster=raw_result.get("style_cluster", ""),
        device_chain=raw_result.get("device_chain", []),
        parameters=raw_result.get("parameters", {}),
        score=total,
        score_breakdown=breakdown,
        provenance=RetrieveProvenance(
            source_dataset="unified_sound_knowledge",
            confidence=total,
        ),
    )


def retrieve(prompt: str, top_k: int = 3) -> RetrieveResponse:
    """Run retrieval and return the Max-friendly response contract."""
    warnings: list[str] = []

    try:
        engine = _get_engine()
    except FileNotFoundError:
        raise  # Let server handle 503

    raw = engine.query(prompt, top_k=top_k)
    raw_results = raw.get("results", [])

    if not raw_results:
        warnings.append("No matching presets found for the given prompt.")

    results = [_build_result(r) for r in raw_results]

    # Warn if top score is low (weak match)
    if results and results[0].score < 0.15:
        warnings.append(
            "Low confidence match. Consider broadening your prompt."
        )

    return RetrieveResponse(
        prompt=prompt,
        results=results,
        warnings=warnings,
    )
