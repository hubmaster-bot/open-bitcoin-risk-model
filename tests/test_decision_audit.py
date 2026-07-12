"""Tests for Decision Intelligence."""

import pandas as pd

from obrm.decision.audit import build_decision_audit, explain_decision


def _row() -> pd.Series:
    return pd.Series(
        {
            "price_position_risk": 0.80,
            "momentum_risk": 0.60,
            "volatility_risk": 0.40,
            "premium_pct": 35.0,
            "return_30d": 0.10,
            "return_90d": 0.20,
            "realised_volatility_30d": 0.50,
            "drawdown_from_ath": -0.10,
            "composite_risk": 0.64,
            "confidence_v1": 0.88,
            "component_coverage": 1.00,
            "component_agreement": 0.60,
            "preliminary_confidence": 0.92,
            "decision_label": "Reduced DCA",
            "decision_action": "dca_in",
        }
    )


def test_primary_driver_uses_largest_weighted_contribution() -> None:
    audit = build_decision_audit(_row())
    assert audit.primary_driver == "Valuation"


def test_contributions_sum_to_composite_risk() -> None:
    audit = build_decision_audit(_row())
    contribution_total = sum(item.contribution for item in audit.dimensions)
    assert contribution_total == audit.composite_risk


def test_explanation_mentions_primary_driver_and_decision() -> None:
    audit = build_decision_audit(_row())
    assert "primary driver" in audit.explanation
    assert "Reduced DCA" in audit.explanation


def test_explain_decision_is_template_driven() -> None:
    audit = build_decision_audit(_row())
    text = explain_decision(
        dimensions=audit.dimensions,
        composite_risk=audit.composite_risk,
        model_confidence=audit.model_confidence,
        decision_label=audit.decision_label,
    )
    assert "Composite Risk" in text
    assert "Model Confidence" in text
