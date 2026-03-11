"""Pydantic models for the /api/retrieve endpoint.

Defines the Max-friendly response contract with normalized 0-1 scoring
and a 5-dimension explainable breakdown.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Request ───────────────────────────────────────────────────────────────────

class RetrieveRequest(BaseModel):
    """POST /api/retrieve request body."""
    prompt: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=3, ge=1, le=10)


# ── Response components ───────────────────────────────────────────────────────

class RetrieveScoreBreakdown(BaseModel):
    """5-dimension normalized score breakdown (0-1 per dimension)."""
    family: float = 0.0
    style_cluster: float = 0.0
    tag_overlap: float = 0.0
    attributes: float = 0.0
    provenance_confidence: float = 0.0


class RetrieveProvenance(BaseModel):
    """Source provenance metadata."""
    source_dataset: str = "unified_sound_knowledge"
    confidence: float = 0.0


class RetrieveResult(BaseModel):
    """A single preset result in the Max-friendly contract."""
    preset_name: str = ""
    family: str = ""
    style_cluster: str = ""
    device_chain: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)
    score: float = 0.0
    score_breakdown: RetrieveScoreBreakdown = Field(
        default_factory=RetrieveScoreBreakdown
    )
    provenance: RetrieveProvenance = Field(default_factory=RetrieveProvenance)


# ── Top-level response ────────────────────────────────────────────────────────

class RetrieveResponse(BaseModel):
    """POST /api/retrieve response body.

    Stable contract designed for Max for Live JS consumption.
    """
    prompt: str
    results: list[RetrieveResult] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
