"""Tests for validated on-chain analytics."""

import numpy as np
import pandas as pd
import pytest

from obrm.onchain.validated_analytics import (
    ValidatedOnChainConfig,
    build_validated_onchain_analytics,
)


def _frame(rows: int = 800) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=rows, freq="D"),
            "CapMVRVCur": np.linspace(0.8, 3.0, rows),
            "HashRate": np.linspace(100.0, 500.0, rows),
            "provider": "Test",
            "asset": "btc",
        }
    )


def test_validated_score_is_bounded() -> None:
    result = build_validated_onchain_analytics(
        _frame(),
        ValidatedOnChainConfig(
            percentile_min_periods=50,
            hash_rate_growth_days=30,
            hash_rate_trend_days=20,
            smoothing_days=5,
        ),
    )

    score = result["onchain_research_score"].dropna()
    assert not score.empty
    assert score.between(0.0, 1.0).all()


def test_hash_rate_growth_uses_only_past_data() -> None:
    result = build_validated_onchain_analytics(
        _frame(100),
        ValidatedOnChainConfig(
            percentile_min_periods=10,
            hash_rate_growth_days=30,
            hash_rate_trend_days=20,
            smoothing_days=5,
        ),
    )

    assert result["hash_rate_growth_365d"].iloc[:30].isna().all()


def test_required_columns_are_enforced() -> None:
    with pytest.raises(ValueError, match="missing columns"):
        build_validated_onchain_analytics(
            pd.DataFrame({"date": pd.date_range("2020-01-01", periods=10)})
        )
