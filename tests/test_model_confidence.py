"""Tests for Model Confidence explainability."""

import pandas as pd

from obrm.confidence.explainability import (
    build_model_confidence_snapshot,
    confidence_explanation,
    confidence_label,
)


def test_confidence_labels() -> None:
    assert confidence_label(0.40) == "Low"
    assert confidence_label(0.65) == "Moderate"
    assert confidence_label(0.80) == "High"
    assert confidence_label(0.95) == "Very High"


def test_confidence_snapshot_uses_existing_engine_values() -> None:
    row = pd.Series(
        {
            "confidence_v1": 0.88,
            "component_coverage": 1.0,
            "component_agreement": 0.75,
            "preliminary_confidence": 0.92,
        }
    )
    snapshot = build_model_confidence_snapshot(row)
    assert snapshot.overall == 0.88
    assert snapshot.coverage == 1.0
    assert snapshot.agreement == 0.75
    assert snapshot.model_maturity == 0.92
    assert snapshot.data_quality == 1.0


def test_confidence_explanation_mentions_strongest_and_weakest() -> None:
    row = pd.Series(
        {
            "confidence_v1": 0.88,
            "component_coverage": 1.0,
            "component_agreement": 0.70,
            "preliminary_confidence": 0.90,
        }
    )
    text = confidence_explanation(build_model_confidence_snapshot(row))
    assert "strongest factor" in text
    assert "weakest factor" in text
