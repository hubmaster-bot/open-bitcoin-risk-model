"""Decision audit and explanation helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from obrm.analytics.explainability import DimensionSnapshot, build_dimension_snapshots
from obrm.confidence.explainability import (
    ModelConfidenceSnapshot,
    build_model_confidence_snapshot,
    confidence_label,
)


@dataclass(frozen=True)
class DecisionAudit:
    composite_risk: float
    model_confidence: float
    decision_label: str
    decision_action: str
    primary_driver: str
    dimensions: tuple[DimensionSnapshot, ...]
    confidence: ModelConfidenceSnapshot
    explanation: str


def build_decision_audit(row: pd.Series) -> DecisionAudit:
    dimensions = build_dimension_snapshots(row)
    confidence = build_model_confidence_snapshot(row)
    primary = max(dimensions, key=lambda dimension: dimension.contribution)
    explanation = explain_decision(
        dimensions=dimensions,
        composite_risk=float(row["composite_risk"]),
        model_confidence=confidence.overall,
        decision_label=str(row["decision_label"]),
    )
    return DecisionAudit(
        composite_risk=float(row["composite_risk"]),
        model_confidence=confidence.overall,
        decision_label=str(row["decision_label"]),
        decision_action=str(row["decision_action"]),
        primary_driver=primary.display_name,
        dimensions=dimensions,
        confidence=confidence,
        explanation=explanation,
    )


def explain_decision(
    *,
    dimensions: tuple[DimensionSnapshot, ...],
    composite_risk: float,
    model_confidence: float,
    decision_label: str,
) -> str:
    primary = max(dimensions, key=lambda item: item.contribution)
    ordered = sorted(dimensions, key=lambda item: item.contribution, reverse=True)
    dimension_text = " ".join(
        f"{item.display_name} is {item.label.lower()} at {item.score:.2f}, "
        f"contributing {item.contribution:.3f}."
        for item in ordered
    )
    return (
        f"{primary.display_name} is the primary driver of the current assessment. "
        f"{dimension_text} These Market Dimensions combine to produce a "
        f"Composite Risk score of {composite_risk:.2f}. Model Confidence is "
        f"{confidence_label(model_confidence).lower()} at {model_confidence:.0%}. "
        f"The Decision Engine therefore recommends: {decision_label}."
    )
