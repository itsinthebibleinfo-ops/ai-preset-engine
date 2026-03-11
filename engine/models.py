"""Pydantic models and typed dicts for the AI Sound Design Engine."""

from __future__ import annotations

from pydantic import BaseModel, Field
from engine.config import DEFAULT_TOP_K, MAX_TOP_K, MAX_PROMPT_LENGTH


# ── Internal data models ──────────────────────────────────────────────────────

class NormalizedPreset(BaseModel):
    """A preset normalised into a common retrieval schema."""
    preset_id: str = ""
    preset_name: str = ""
    genre: str = ""
    subgenre: str = ""
    family: str = ""
    style_cluster: str = ""
    tags: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    device_chain: list[str] = Field(default_factory=list)
    parameters: dict = Field(default_factory=dict)


class ParsedQuery(BaseModel):
    """The structured result of parsing a natural-language prompt."""
    family: str | None = None
    genre: str | None = None
    subgenre: str | None = None
    style_clusters: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    attributes: list[str] = Field(default_factory=list)


# ── API models ────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    """POST /generate request body."""
    prompt: str = Field(..., min_length=1, max_length=MAX_PROMPT_LENGTH)
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=MAX_TOP_K)


class GenerateResponse(BaseModel):
    """POST /generate response body."""
    prompt: str
    top_k: int
    count: int
    recommended_presets: list[dict]


class HealthResponse(BaseModel):
    """GET / response body."""
    status: str = "ok"
    message: str = "Ableton AI Preset Engine is running"
    preset_count: int = 0


# ── Enhanced v2 models ────────────────────────────────────────────────────────

class ScoreBreakdownModel(BaseModel):
    """8-dimensional explainable score breakdown."""
    family: float = 0.0
    genre: float = 0.0
    subgenre: float = 0.0
    style_cluster: float = 0.0
    tag_overlap: float = 0.0
    attribute_alignment: float = 0.0
    mood: float = 0.0
    provenance: float = 0.0


class EnhancedResult(BaseModel):
    """A single ranked preset with full score breakdown."""
    rank: int
    preset_id: str = ""
    preset_name: str = ""
    family: str = ""
    genre: str = ""
    style_cluster: str = ""
    tags: list[str] = Field(default_factory=list)
    score: float = 0.0
    breakdown: ScoreBreakdownModel = Field(default_factory=ScoreBreakdownModel)
    device_chain: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    parameters: dict = Field(default_factory=dict)


class ParsedPromptModel(BaseModel):
    """Structured parse of the user prompt."""
    raw: str
    parsed_family: str | None = None
    parsed_genre: str | None = None
    parsed_subgenre: str | None = None
    parsed_tags: list[str] = Field(default_factory=list)
    parsed_moods: list[str] = Field(default_factory=list)
    style_cluster_hints: list[str] = Field(default_factory=list)
    unknown_tokens: list[str] = Field(default_factory=list)


class EnhancedMetadata(BaseModel):
    """Query metadata."""
    total_presets_searched: int = 0
    results_returned: int = 0
    top_score: float = 0.0


class EnhancedGenerateResponse(BaseModel):
    """POST /v2/generate response with explainable scoring."""
    query: ParsedPromptModel
    results: list[EnhancedResult] = Field(default_factory=list)
    metadata: EnhancedMetadata = Field(default_factory=EnhancedMetadata)
