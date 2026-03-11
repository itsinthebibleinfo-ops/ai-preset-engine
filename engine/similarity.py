"""Similarity scoring between a parsed query and a normalised preset."""

from __future__ import annotations

from engine.config import (
    WEIGHT_ATTRIBUTE,
    WEIGHT_FAMILY,
    WEIGHT_GENRE,
    WEIGHT_STYLE_CLUSTER,
    WEIGHT_SUBGENRE,
    WEIGHT_TAG,
)


def score_preset(query: dict, preset: dict) -> float:
    """Return a relevance score (higher = better match)."""
    score = 0.0

    preset_family = str(preset.get("family", "")).lower()
    preset_genre = str(preset.get("genre", "")).lower()
    preset_subgenre = str(preset.get("subgenre", "")).lower()
    preset_style = str(preset.get("style_cluster", "")).lower()
    preset_tags = {str(x).lower() for x in preset.get("tags", [])}

    preset_attributes = preset.get("attributes", {})
    if not isinstance(preset_attributes, dict):
        preset_attributes = {}

    query_family = query.get("family")
    query_genre = query.get("genre")
    query_subgenre = query.get("subgenre")
    query_style_clusters = {str(x).lower() for x in query.get("style_clusters", [])}
    query_tags = {str(x).lower() for x in query.get("tags", [])}
    query_attributes = {str(x).lower() for x in query.get("attributes", [])}

    # Family match
    if query_family and query_family == preset_family:
        score += WEIGHT_FAMILY

    # Genre match
    if query_genre and query_genre in preset_genre:
        score += WEIGHT_GENRE

    # Subgenre match
    if query_subgenre and query_subgenre in preset_subgenre:
        score += WEIGHT_SUBGENRE

    # Style-cluster match
    if preset_style and preset_style in query_style_clusters:
        score += WEIGHT_STYLE_CLUSTER

    # Tag overlap
    tag_overlap = len(query_tags.intersection(preset_tags))
    score += tag_overlap * WEIGHT_TAG

    # Attribute-key overlap
    attribute_keys = {str(k).lower() for k in preset_attributes.keys()}
    attribute_overlap = len(query_attributes.intersection(attribute_keys))
    score += attribute_overlap * WEIGHT_ATTRIBUTE

    return score
