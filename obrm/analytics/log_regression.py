"""Expanding logarithmic regression for Bitcoin fair value."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


SECONDS_PER_DAY = 86_400


@dataclass(frozen=True)
class LogRegressionConfig:
    """Configuration for the expanding fair-value model."""

    genesis_date: str = "2009-01-03"
    minimum_observations: int = 730
    risk_sensitivity: float = 1.35


def _sigmoid(values: pd.Series, sensitivity: float) -> pd.Series:
    """Map signed z-scores to a bounded 0–1 risk scale."""
    clipped = values.clip(-8.0, 8.0)
    return 1.0 / (1.0 + np.exp(-sensitivity * clipped))


def calculate_log_regression(
    price_data: pd.DataFrame,
    config: LogRegressionConfig | None = None,
) -> pd.DataFrame:
    """Calculate expanding log-log fair value without future data leakage.

    The model fits:

        log10(price) = intercept + slope * log10(days since genesis)

    For each date, cumulative OLS statistics use only observations available
    on or before that date. The first ``minimum_observations`` rows are treated
    as warm-up and do not receive model outputs.
    """
    cfg = config or LogRegressionConfig()

    required = {"date", "price_usd"}
    missing = required - set(price_data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df = price_data.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["price_usd"] = pd.to_numeric(df["price_usd"], errors="coerce")
    df = (
        df.dropna(subset=["date", "price_usd"])
        .loc[lambda frame: frame["price_usd"] > 0]
        .sort_values("date")
        .reset_index(drop=True)
    )

    genesis = pd.Timestamp(cfg.genesis_date)
    days_since_genesis = (df["date"] - genesis).dt.total_seconds() / SECONDS_PER_DAY
    if (days_since_genesis <= 0).any():
        raise ValueError("All observations must occur after the configured genesis date.")

    x = np.log10(days_since_genesis.to_numpy(dtype=float))
    y = np.log10(df["price_usd"].to_numpy(dtype=float))

    n = np.arange(1, len(df) + 1, dtype=float)
    sum_x = np.cumsum(x)
    sum_y = np.cumsum(y)
    sum_xx = np.cumsum(x * x)
    sum_xy = np.cumsum(x * y)
    sum_yy = np.cumsum(y * y)

    denominator = n * sum_xx - sum_x * sum_x
    slope = np.full(len(df), np.nan)
    intercept = np.full(len(df), np.nan)

    valid = denominator > 0
    slope[valid] = (n[valid] * sum_xy[valid] - sum_x[valid] * sum_y[valid]) / denominator[valid]
    intercept[valid] = (sum_y[valid] - slope[valid] * sum_x[valid]) / n[valid]

    fitted_log_price = intercept + slope * x
    fair_value = np.power(10.0, fitted_log_price)
    residual = y - fitted_log_price

    # Expanding residual statistics. Because each fitted value is generated from
    # the expanding model available on that date, this remains no-look-ahead.
    residual_series = pd.Series(residual)
    residual_mean = residual_series.expanding(min_periods=cfg.minimum_observations).mean()
    residual_std = residual_series.expanding(min_periods=cfg.minimum_observations).std(ddof=1)
    residual_z = (residual_series - residual_mean) / residual_std.replace(0.0, np.nan)

    # Expanding R² from cumulative sums.
    ss_tot = sum_yy - (sum_y * sum_y / n)
    ss_res = np.full(len(df), np.nan)
    ss_res[valid] = (
        sum_yy[valid]
        + n[valid] * intercept[valid] ** 2
        + slope[valid] ** 2 * sum_xx[valid]
        + 2.0 * intercept[valid] * slope[valid] * sum_x[valid]
        - 2.0 * intercept[valid] * sum_y[valid]
        - 2.0 * slope[valid] * sum_xy[valid]
    )
    r_squared = np.where(ss_tot > 0, 1.0 - (ss_res / ss_tot), np.nan)

    warmup_mask = n < cfg.minimum_observations
    fair_value[warmup_mask] = np.nan
    slope[warmup_mask] = np.nan
    intercept[warmup_mask] = np.nan
    r_squared[warmup_mask] = np.nan
    residual_z.loc[warmup_mask] = np.nan

    result = df.copy()
    result["fair_value_usd"] = fair_value
    result["premium_pct"] = ((result["price_usd"] / result["fair_value_usd"]) - 1.0) * 100.0
    result["trend_residual_z"] = residual_z
    result["price_position_risk"] = _sigmoid(
        result["trend_residual_z"],
        cfg.risk_sensitivity,
    )
    result["regression_r_squared"] = r_squared.clip(0.0, 1.0)

    # Preliminary confidence for v0.4.0. This is explicitly model-quality
    # confidence, not a probability of future returns.
    sample_strength = np.clip(
        (n - cfg.minimum_observations + 1.0) / (365.0 * 4.0),
        0.0,
        1.0,
    )
    result["preliminary_confidence"] = (
        0.70 * result["regression_r_squared"].fillna(0.0)
        + 0.30 * sample_strength
    ).clip(0.0, 1.0)

    result.loc[warmup_mask, "preliminary_confidence"] = np.nan
    return result
