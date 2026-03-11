"""FastAPI application for the AI Sound Design Engine."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from engine.config import load_genres, load_sound_families, load_style_clusters
from engine.models import (
    EnhancedGenerateResponse,
    EnhancedMetadata,
    EnhancedResult,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    ParsedPromptModel,
    ScoreBreakdownModel,
)
from engine.query_models import RetrieveRequest, RetrieveResponse
from engine.preset_retriever import load_presets, retrieve_presets

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ableton AI Preset Engine",
    version="0.2.0",
    description="Natural-language preset retrieval for Ableton Live.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse)
def root():
    """Health check — also reports how many presets are loaded."""
    try:
        count = len(load_presets())
    except Exception:
        count = 0
    return HealthResponse(preset_count=count)


@app.get("/taxonomy")
def taxonomy():
    """Return the current taxonomy (genres, families, style clusters)."""
    return {
        "genres": load_genres(),
        "sound_families": load_sound_families(),
        "style_clusters": load_style_clusters(),
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    """Retrieve presets matching a natural-language prompt."""
    try:
        results = retrieve_presets(req.prompt, top_k=req.top_k)
        return GenerateResponse(
            prompt=req.prompt,
            top_k=req.top_k,
            count=len(results),
            recommended_presets=results,
        )
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="Preset database not found")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in /generate")
        raise HTTPException(status_code=500, detail=str(e))


# ── Max bridge endpoint ───────────────────────────────────────────────────────

@app.post("/api/retrieve", response_model=RetrieveResponse)
def api_retrieve(req: RetrieveRequest):
    """Max-friendly preset retrieval with normalized 0-1 scoring.

    Designed for consumption by Max for Live JS bridge.
    Returns a stable contract with 5-dimension score breakdown.
    """
    try:
        from engine.retrieval_api import retrieve
        return retrieve(req.prompt, top_k=req.top_k)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Unified knowledge database not found. Run build_unified_knowledge first.",
        )
    except Exception as e:
        logger.exception("Unexpected error in /api/retrieve")
        raise HTTPException(status_code=500, detail=str(e))


# ── Enhanced v2 endpoint ──────────────────────────────────────────────────────

_retrieval_engine = None


def _get_retrieval_engine():
    """Lazy singleton for the enhanced retrieval engine."""
    global _retrieval_engine
    if _retrieval_engine is None:
        from sound_lab.scripts.retrieval_engine import RetrievalEngine
        _retrieval_engine = RetrievalEngine()
    return _retrieval_engine


@app.post("/v2/generate", response_model=EnhancedGenerateResponse)
def generate_v2(req: GenerateRequest):
    """Enhanced preset retrieval with explainable 8-dimensional scoring."""
    try:
        engine = _get_retrieval_engine()
        raw = engine.query(req.prompt, top_k=req.top_k)

        query_model = ParsedPromptModel(**raw["query"])
        results = [
            EnhancedResult(
                rank=r["rank"],
                preset_id=r["preset_id"],
                preset_name=r["preset_name"],
                family=r["family"],
                genre=r["genre"],
                style_cluster=r["style_cluster"],
                tags=r["tags"],
                score=r["score"],
                breakdown=ScoreBreakdownModel(**r["breakdown"]),
                device_chain=r["device_chain"],
                attributes=r["attributes"],
                parameters=r["parameters"],
            )
            for r in raw["results"]
        ]
        metadata = EnhancedMetadata(**raw["metadata"])

        return EnhancedGenerateResponse(
            query=query_model,
            results=results,
            metadata=metadata,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Unified knowledge database not found. Run build_unified_knowledge first.",
        )
    except Exception as e:
        logger.exception("Unexpected error in /v2/generate")
        raise HTTPException(status_code=500, detail=str(e))
