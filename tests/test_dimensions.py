"""Tests for Market Dimension terminology and explanations."""

import pandas as pd

from obrm.analytics.dimensions import MARKET_DIMENSIONS, explain_dimension, score_label
from obrm.analytics.explainability import build_dimension_snapshots


def test_standard_score_labels() -> None:
    assert score_label(0.10) == "Deep Value"
    assert score_label(0.30) == "Attractive"
    assert score_label(0.50) == "Neutral"
    assert score_label(0.70) == "Elevated"
    assert score_label(0.85) == "High"
    assert score_label(0.95) == "Extreme"


def test_registered_weights_sum_to_one() -> None:
    assert sum(item.weight for item in MARKET_DIMENSIONS) == 1.0


def test_valuation_explanation_uses_premium() -> None:
    text = explain_dimension("valuation", 0.85, premium_pct=45.0)
    assert "materially above" in text
    assert "+45.0%" in text


def test_dimension_snapshots_include_contribution() -> None:
    row = pd.Series(
        {
            "price_position_risk": 0.8,
            "momentum_risk": 0.6,
            "volatility_risk": 0.4,
            "premium_pct": 35.0,
            "return_30d": 0.1,
            "return_90d": 0.2,
            "realised_volatility_30d": 0.5,
            "drawdown_from_ath": -0.1,
        }
    )
    snapshots = build_dimension_snapshots(row)
    assert len(snapshots) == 3
    assert snapshots[0].contribution == 0.8 * 0.45
