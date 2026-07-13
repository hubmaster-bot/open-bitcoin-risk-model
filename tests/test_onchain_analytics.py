"""Tests for v0.9.1 on-chain analytics."""

import numpy as np
import pandas as pd

from obrm.onchain.analytics import (
    OnChainAnalyticsConfig,
    calculate_onchain_analytics,
)
from obrm.onchain.registry import MetricResolution, ResolvedMetric


def _resolution() -> MetricResolution:
    return MetricResolution(
        resolved=(
            ResolvedMetric(
                "realized_cap_usd",
                "Realized Capitalization",
                "CapRealUSD",
                "test",
                True,
            ),
            ResolvedMetric(
                "mvrv",
                "MVRV",
                "CapMVRVCur",
                "test",
                True,
            ),
        ),
        unresolved_required=(),
        unresolved_optional=("Supply Active in One Year",),
    )


def test_analytics_are_bounded_and_no_lookahead() -> None:
    dates = pd.date_range("2020-01-01", periods=800, freq="D")
    frame = pd.DataFrame(
        {
            "date": dates,
            "CapRealUSD": np.linspace(100, 1000, len(dates)),
            "CapMVRVCur": np.linspace(0.8, 3.0, len(dates)),
            "provider": "Test",
            "asset": "btc",
        }
    )
    result = calculate_onchain_analytics(
        frame,
        _resolution(),
        OnChainAnalyticsConfig(
            realized_cap_growth_days=30,
            percentile_min_periods=50,
            smoothing_days=5,
        ),
    )

    score = result["onchain_research_score"].dropna()
    assert not score.empty
    assert score.between(0.0, 1.0).all()
    assert result["realized_cap_growth_365d"].iloc[:30].isna().all()


def test_required_metric_is_enforced() -> None:
    resolution = MetricResolution(
        resolved=(),
        unresolved_required=("MVRV",),
        unresolved_optional=(),
    )
    frame = pd.DataFrame({"date": pd.date_range("2020-01-01", periods=10)})

    try:
        calculate_onchain_analytics(frame, resolution)
    except ValueError as exc:
        assert "Realized Capitalization" in str(exc)
    else:
        raise AssertionError("Expected missing required metric to fail.")
