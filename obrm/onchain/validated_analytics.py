"""Validated v0.9.3 on-chain research analytics."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ValidatedOnChainConfig:
    percentile_min_periods: int = 365
    hash_rate_growth_days: int = 365
    hash_rate_trend_days: int = 200
    smoothing_days: int = 30


def expanding_percentile(
    series: pd.Series,
    *,
    min_periods: int,
) -> pd.Series:
    """Calculate a no-look-ahead expanding percentile rank."""
    values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    output = np.full(len(values), np.nan)

    for index, value in enumerate(values):
        history = values[: index + 1]
        valid = history[np.isfinite(history)]
        if len(valid) < min_periods or not np.isfinite(value):
            continue
        output[index] = float(np.mean(valid <= value))

    return pd.Series(output, index=series.index, dtype=float)


def build_validated_onchain_analytics(
    frame: pd.DataFrame,
    config: ValidatedOnChainConfig | None = None,
) -> pd.DataFrame:
    """Build research signals from empirically available Community metrics."""
    cfg = config or ValidatedOnChainConfig()
    required = {"date", "CapMVRVCur", "HashRate"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            "Validated on-chain dataset is missing columns: "
            + ", ".join(sorted(missing))
        )

    df = frame.copy().sort_values("date").reset_index(drop=True)
    df["mvrv"] = pd.to_numeric(df["CapMVRVCur"], errors="coerce")
    df["hash_rate"] = pd.to_numeric(df["HashRate"], errors="coerce")

    df["mvrv_percentile"] = expanding_percentile(
        df["mvrv"],
        min_periods=cfg.percentile_min_periods,
    )

    df["hash_rate_growth_365d"] = df["hash_rate"].pct_change(
        cfg.hash_rate_growth_days
    )
    df["hash_rate_trend"] = df["hash_rate"].rolling(
        cfg.hash_rate_trend_days,
        min_periods=cfg.hash_rate_trend_days,
    ).mean()
    df["hash_rate_vs_trend"] = (
        df["hash_rate"] / df["hash_rate_trend"] - 1.0
    )

    df["hash_rate_growth_percentile"] = expanding_percentile(
        df["hash_rate_growth_365d"],
        min_periods=cfg.percentile_min_periods,
    )
    df["hash_rate_trend_percentile"] = expanding_percentile(
        df["hash_rate_vs_trend"],
        min_periods=cfg.percentile_min_periods,
    )

    df["network_strength_score"] = (
        df[
            [
                "hash_rate_growth_percentile",
                "hash_rate_trend_percentile",
            ]
        ]
        .mean(axis=1, skipna=True)
        .clip(0.0, 1.0)
    )

    # Higher MVRV implies more elevated realized valuation conditions.
    df["realized_valuation_score"] = df["mvrv_percentile"].clip(0.0, 1.0)

    component_columns = [
        "realized_valuation_score",
        "network_strength_score",
    ]
    df["onchain_research_score"] = (
        df[component_columns]
        .mean(axis=1, skipna=True)
        .rolling(cfg.smoothing_days, min_periods=1)
        .mean()
        .clip(0.0, 1.0)
    )
    df["onchain_input_coverage"] = (
        df[component_columns].notna().mean(axis=1)
    )

    return df
