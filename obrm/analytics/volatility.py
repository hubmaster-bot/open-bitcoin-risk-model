"""Volatility analytics for OBRM."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class VolatilityConfig:
    realised_window_days: int = 30
    annualisation_days: int = 365
    percentile_min_periods: int = 365
    drawdown_weight: float = 0.45
    realised_volatility_weight: float = 0.55


def _percentile_rank_expanding(series: pd.Series, min_periods: int) -> pd.Series:
    """Expanding percentile rank without future leakage."""
    values = series.to_numpy(dtype=float)
    output = np.full(len(series), np.nan)

    for idx in range(len(values)):
        history = values[: idx + 1]
        valid = history[np.isfinite(history)]
        if len(valid) < min_periods or not np.isfinite(values[idx]):
            continue
        output[idx] = np.mean(valid <= values[idx])

    return pd.Series(output, index=series.index, dtype=float)


def calculate_volatility_risk(
    price_data: pd.DataFrame,
    config: VolatilityConfig | None = None,
) -> pd.DataFrame:
    """Calculate realised-volatility and drawdown-based risk."""
    cfg = config or VolatilityConfig()
    df = price_data.copy()
    prices = pd.to_numeric(df["price_usd"], errors="coerce")

    log_returns = np.log(prices / prices.shift(1))
    df["realised_volatility_30d"] = (
        log_returns.rolling(
            cfg.realised_window_days,
            min_periods=cfg.realised_window_days,
        ).std(ddof=1)
        * np.sqrt(cfg.annualisation_days)
    )

    running_ath = prices.cummax()
    df["drawdown_from_ath"] = (prices / running_ath) - 1.0

    vol_rank = _percentile_rank_expanding(
        df["realised_volatility_30d"],
        min_periods=cfg.percentile_min_periods,
    )

    # A small drawdown implies elevated late-cycle conditions; a deep drawdown
    # implies lower current market risk.
    drawdown_risk = (1.0 + df["drawdown_from_ath"]).clip(0.0, 1.0)

    df["volatility_risk"] = (
        cfg.realised_volatility_weight * vol_rank
        + cfg.drawdown_weight * drawdown_risk
    ).clip(0.0, 1.0)

    return df
