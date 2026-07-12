"""Tests for walk-forward validation."""

import numpy as np
import pandas as pd

from obrm.research.validation import (
    ValidationConfig,
    add_forward_returns,
    calibration_table,
    forward_return_summary,
    monotonicity_score,
)


def _analytics() -> pd.DataFrame:
    rows = 1200
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    price = 100.0 * np.exp(np.linspace(0.0, 2.0, rows))
    risk = np.linspace(0.05, 0.95, rows)

    return pd.DataFrame(
        {
            "date": dates,
            "price_usd": price,
            "composite_risk": risk,
            "confidence_v1": 0.90,
        }
    )


def test_forward_returns_are_outcome_columns() -> None:
    result = add_forward_returns(_analytics(), (90, 365))
    assert result["forward_return_90d"].tail(90).isna().all()
    assert result["forward_return_365d"].tail(365).isna().all()


def test_forward_return_summary_has_all_risk_bands() -> None:
    config = ValidationConfig(forward_days=(90,))
    result = forward_return_summary(_analytics(), config)
    assert set(result["risk_band"]) == set(config.risk_labels)


def test_monotonicity_score_is_bounded() -> None:
    summary = forward_return_summary(
        _analytics(),
        ValidationConfig(forward_days=(90,)),
    )
    score = monotonicity_score(summary, 90)
    assert 0.0 <= score <= 1.0


def test_calibration_table_contains_outcome_frequency() -> None:
    result = calibration_table(_analytics())
    assert "negative_365d_outcomes_pct" in result.columns
    assert "median_365d_return_pct" in result.columns
