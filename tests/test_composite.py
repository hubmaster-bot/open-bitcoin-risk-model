"""Tests for composite risk and confidence."""

import pandas as pd
import pytest

from obrm.analytics.composite import (
    CompositeRiskConfig,
    calculate_composite_risk,
)


def test_composite_risk_uses_configured_weights() -> None:
    df = pd.DataFrame(
        {
            "price_position_risk": [0.2],
            "momentum_risk": [0.6],
            "volatility_risk": [0.8],
            "preliminary_confidence": [0.9],
        }
    )

    result = calculate_composite_risk(df)
    expected = 0.45 * 0.2 + 0.30 * 0.6 + 0.25 * 0.8

    assert result.loc[0, "composite_risk"] == pytest.approx(expected)
    assert 0.0 <= result.loc[0, "confidence_v1"] <= 1.0


def test_invalid_weights_are_rejected() -> None:
    with pytest.raises(ValueError, match="sum to 1.0"):
        calculate_composite_risk(
            pd.DataFrame(
                {
                    "price_position_risk": [0.2],
                    "momentum_risk": [0.4],
                    "volatility_risk": [0.6],
                    "preliminary_confidence": [0.8],
                }
            ),
            CompositeRiskConfig(0.5, 0.5, 0.5),
        )
