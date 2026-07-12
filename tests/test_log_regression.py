"""Tests for the v0.4.0 log regression model."""

import numpy as np
import pandas as pd

from obrm.analytics.log_regression import (
    LogRegressionConfig,
    calculate_log_regression,
)


def _synthetic_prices(rows: int = 900) -> pd.DataFrame:
    dates = pd.date_range("2010-01-01", periods=rows, freq="D")
    days = (dates - pd.Timestamp("2009-01-03")).days.astype(float)
    fair_value = 0.01 * np.power(days, 1.5)

    return pd.DataFrame(
        {
            "date": dates,
            "price_usd": fair_value,
            "provider": ["Synthetic"] * rows,
        }
    )


def test_model_respects_warmup_period() -> None:
    df = _synthetic_prices()
    result = calculate_log_regression(
        df,
        LogRegressionConfig(minimum_observations=100),
    )

    assert result.loc[:98, "fair_value_usd"].isna().all()
    assert result.loc[99:, "fair_value_usd"].notna().all()


def test_perfect_log_power_series_has_high_fit() -> None:
    df = _synthetic_prices()
    result = calculate_log_regression(
        df,
        LogRegressionConfig(minimum_observations=100),
    )

    latest = result.dropna(subset=["regression_r_squared"]).iloc[-1]
    assert latest["regression_r_squared"] > 0.999
    assert abs(latest["premium_pct"]) < 0.1


def test_risk_is_bounded() -> None:
    df = _synthetic_prices()
    df.loc[df.index[-30:], "price_usd"] *= 3.0

    result = calculate_log_regression(
        df,
        LogRegressionConfig(minimum_observations=100),
    )
    risk = result["price_position_risk"].dropna()

    assert risk.between(0.0, 1.0).all()
