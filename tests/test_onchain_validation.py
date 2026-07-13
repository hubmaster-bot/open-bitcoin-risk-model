"""Tests for the On-Chain Validation Lab."""

import numpy as np
import pandas as pd

from obrm.validation.onchain_validation import (
    build_onchain_validation_report,
    monotonicity_ratio,
)


def _market(rows: int = 900) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "price_usd": np.linspace(100.0, 1000.0, rows),
            "price_position_risk": np.linspace(0.1, 0.9, rows),
            "momentum_risk": np.linspace(0.2, 0.8, rows),
            "volatility_risk": np.linspace(0.3, 0.7, rows),
            "composite_risk": np.linspace(0.2, 0.8, rows),
        }
    )


def _onchain(rows: int = 900) -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=rows, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "mvrv": np.linspace(0.8, 3.0, rows),
            "hash_rate": np.linspace(100.0, 500.0, rows),
            "realized_valuation_score": np.linspace(0.1, 0.9, rows),
            "network_strength_score": np.linspace(0.2, 0.8, rows),
            "onchain_research_score": np.linspace(0.15, 0.85, rows),
            "onchain_input_coverage": 1.0,
        }
    )


def test_validation_report_builds() -> None:
    report = build_onchain_validation_report(
        _market(),
        _onchain(),
        horizons=(30, 90, 365),
    )

    assert report.usable_rows == 900
    assert not report.bucket_summary.empty
    assert not report.correlations.empty
    assert set(report.subdimension_bucket_summary) == {
        "Realized Valuation",
        "Network Strength",
    }


def test_monotonicity_ratio_rewards_descending_returns() -> None:
    summary = pd.DataFrame(
        {"365d_mean": [1.0, 0.8, 0.5, 0.2, -0.1]}
    )
    assert monotonicity_ratio(summary, "365d_mean") == 1.0
