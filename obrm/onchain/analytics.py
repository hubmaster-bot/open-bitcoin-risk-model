"""Transparent on-chain analytics derived from canonical Coin Metrics data."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from obrm.onchain.registry import MetricResolution


@dataclass(frozen=True)
class OnChainAnalyticsConfig:
    realized_cap_growth_days: int = 365
    percentile_min_periods: int = 365
    smoothing_days: int = 30


def _expanding_percentile(
    series: pd.Series,
    min_periods: int,
) -> pd.Series:
    """No-look-ahead expanding percentile rank."""
    values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    output = np.full(len(values), np.nan)

    for index, value in enumerate(values):
        history = values[: index + 1]
        valid = history[np.isfinite(history)]
        if len(valid) < min_periods or not np.isfinite(value):
            continue
        output[index] = float(np.mean(valid <= value))

    return pd.Series(output, index=series.index, dtype=float)


def calculate_onchain_analytics(
    frame: pd.DataFrame,
    resolution: MetricResolution,
    config: OnChainAnalyticsConfig | None = None,
) -> pd.DataFrame:
    """Calculate v0.9.1 research signals without changing Composite Risk."""
    cfg = config or OnChainAnalyticsConfig()
    df = frame.copy().sort_values("date").reset_index(drop=True)

    metric_map = {
        item.key: item.provider_metric
        for item in resolution.resolved
    }

    if "realized_cap_usd" not in metric_map:
        raise ValueError("Realized Capitalization is required.")
    if "mvrv" not in metric_map:
        raise ValueError("MVRV is required.")

    realized_cap = pd.to_numeric(
        df[metric_map["realized_cap_usd"]],
        errors="coerce",
    )
    mvrv = pd.to_numeric(df[metric_map["mvrv"]], errors="coerce")

    df["realized_cap_usd"] = realized_cap
    df["mvrv"] = mvrv
    df["realized_cap_growth_365d"] = realized_cap.pct_change(
        cfg.realized_cap_growth_days
    )
    df["mvrv_percentile"] = _expanding_percentile(
        mvrv,
        cfg.percentile_min_periods,
    )
    df["realized_cap_growth_percentile"] = _expanding_percentile(
        df["realized_cap_growth_365d"],
        cfg.percentile_min_periods,
    )

    if "active_supply_1y" in metric_map:
        active = pd.to_numeric(
            df[metric_map["active_supply_1y"]],
            errors="coerce",
        )
        df["active_supply_1y"] = active
        df["active_supply_1y_percentile"] = _expanding_percentile(
            active,
            cfg.percentile_min_periods,
        )
    else:
        df["active_supply_1y"] = np.nan
        df["active_supply_1y_percentile"] = np.nan

    available_components = [
        "mvrv_percentile",
        "realized_cap_growth_percentile",
    ]
    if df["active_supply_1y_percentile"].notna().any():
        available_components.append("active_supply_1y_percentile")

    df["onchain_research_score"] = (
        df[available_components]
        .mean(axis=1, skipna=True)
        .rolling(cfg.smoothing_days, min_periods=1)
        .mean()
        .clip(0.0, 1.0)
    )

    df["onchain_component_coverage"] = (
        df[available_components].notna().mean(axis=1)
    )

    return df
