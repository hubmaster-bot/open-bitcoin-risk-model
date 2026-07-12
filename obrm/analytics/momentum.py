"""Momentum analytics for OBRM."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class MomentumConfig:
    short_return_days: int = 30
    medium_return_days: int = 90
    long_ma_days: int = 200
    smoothing_days: int = 14


def _percentile_rank_expanding(series: pd.Series, min_periods: int) -> pd.Series:
    """Expanding percentile rank without future leakage."""
    values = series.to_numpy(dtype=float)
    output = np.full(len(series), np.nan)

    for idx in range(len(values)):
        start = values[: idx + 1]
        valid = start[np.isfinite(start)]
        if len(valid) < min_periods or not np.isfinite(values[idx]):
            continue
        output[idx] = np.mean(valid <= values[idx])

    return pd.Series(output, index=series.index, dtype=float)


def calculate_momentum_risk(
    price_data: pd.DataFrame,
    config: MomentumConfig | None = None,
) -> pd.DataFrame:
    """Calculate a transparent 0-1 momentum risk component."""
    cfg = config or MomentumConfig()
    df = price_data.copy()
    prices = pd.to_numeric(df["price_usd"], errors="coerce")

    df["return_30d"] = prices.pct_change(cfg.short_return_days)
    df["return_90d"] = prices.pct_change(cfg.medium_return_days)
    df["ma_200d"] = prices.rolling(cfg.long_ma_days, min_periods=cfg.long_ma_days).mean()
    df["distance_from_200d_ma"] = (prices / df["ma_200d"]) - 1.0

    short_rank = _percentile_rank_expanding(
        df["return_30d"],
        min_periods=cfg.long_ma_days,
    )
    medium_rank = _percentile_rank_expanding(
        df["return_90d"],
        min_periods=cfg.long_ma_days,
    )
    ma_rank = _percentile_rank_expanding(
        df["distance_from_200d_ma"],
        min_periods=cfg.long_ma_days,
    )

    raw = 0.25 * short_rank + 0.35 * medium_rank + 0.40 * ma_rank
    df["momentum_risk"] = (
        raw.rolling(cfg.smoothing_days, min_periods=1).mean().clip(0.0, 1.0)
    )
    return df
