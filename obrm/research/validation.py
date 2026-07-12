"""Walk-forward validation and historical outcome analysis."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ValidationConfig:
    forward_days: tuple[int, ...] = (90, 365, 730)
    minimum_confidence: float = 0.55
    risk_bins: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.75, 0.85, 0.95, 1.0)
    risk_labels: tuple[str, ...] = (
        "Deep Value",
        "Accumulation",
        "Neutral",
        "Caution",
        "Late Bull",
        "Distribution",
        "Extreme Risk",
    )


def add_forward_returns(
    analytics: pd.DataFrame,
    horizons: tuple[int, ...] = (90, 365, 730),
) -> pd.DataFrame:
    """Add future returns as outcome labels only."""
    df = analytics.copy().sort_values("date").reset_index(drop=True)
    price = pd.to_numeric(df["price_usd"], errors="coerce")

    for days in horizons:
        df[f"forward_return_{days}d"] = (price.shift(-days) / price) - 1.0

    return df


def assign_risk_bands(
    analytics: pd.DataFrame,
    config: ValidationConfig | None = None,
) -> pd.DataFrame:
    cfg = config or ValidationConfig()
    df = analytics.copy()
    df["validation_risk_band"] = pd.cut(
        df["composite_risk"],
        bins=cfg.risk_bins,
        labels=cfg.risk_labels,
        include_lowest=True,
        right=True,
    )
    return df


def forward_return_summary(
    analytics: pd.DataFrame,
    config: ValidationConfig | None = None,
) -> pd.DataFrame:
    cfg = config or ValidationConfig()
    df = add_forward_returns(analytics, cfg.forward_days)
    df = assign_risk_bands(df, cfg)
    df = df.loc[df["confidence_v1"] >= cfg.minimum_confidence].copy()

    rows: list[dict[str, object]] = []

    for band in cfg.risk_labels:
        subset = df.loc[df["validation_risk_band"] == band]

        for horizon in cfg.forward_days:
            column = f"forward_return_{horizon}d"
            values = subset[column].dropna()

            rows.append(
                {
                    "risk_band": band,
                    "horizon_days": horizon,
                    "observations": int(len(values)),
                    "median_return_pct": float(values.median() * 100.0) if len(values) else np.nan,
                    "mean_return_pct": float(values.mean() * 100.0) if len(values) else np.nan,
                    "positive_outcomes_pct": float((values > 0).mean() * 100.0) if len(values) else np.nan,
                    "worst_return_pct": float(values.min() * 100.0) if len(values) else np.nan,
                    "best_return_pct": float(values.max() * 100.0) if len(values) else np.nan,
                }
            )

    return pd.DataFrame(rows)


def monotonicity_score(
    summary: pd.DataFrame,
    horizon_days: int = 365,
) -> float:
    """Return 0-1 score for declining returns as risk rises."""
    subset = (
        summary.loc[summary["horizon_days"] == horizon_days]
        .dropna(subset=["median_return_pct"])
        .reset_index(drop=True)
    )

    if len(subset) < 2:
        return float("nan")

    values = subset["median_return_pct"].to_numpy(dtype=float)
    return float((values[:-1] >= values[1:]).mean())


def calibration_table(
    analytics: pd.DataFrame,
    config: ValidationConfig | None = None,
) -> pd.DataFrame:
    cfg = config or ValidationConfig()
    df = add_forward_returns(analytics, (365,))
    df = assign_risk_bands(df, cfg)
    df = df.loc[df["confidence_v1"] >= cfg.minimum_confidence].copy()

    return (
        df.groupby("validation_risk_band", observed=False)
        .agg(
            observations=("forward_return_365d", "count"),
            average_risk=("composite_risk", "mean"),
            negative_365d_outcomes_pct=(
                "forward_return_365d",
                lambda values: float((values.dropna() < 0).mean() * 100.0)
                if len(values.dropna()) else np.nan,
            ),
            median_365d_return_pct=(
                "forward_return_365d",
                lambda values: float(values.dropna().median() * 100.0)
                if len(values.dropna()) else np.nan,
            ),
        )
        .reset_index()
    )


def cycle_summary(analytics: pd.DataFrame) -> pd.DataFrame:
    df = analytics.copy()
    df["date"] = pd.to_datetime(df["date"])

    eras = (
        ("Early market", "2012-01-01", "2015-12-31"),
        ("2016-2018 cycle", "2016-01-01", "2018-12-31"),
        ("2019-2022 cycle", "2019-01-01", "2022-12-31"),
        ("2023 onward", "2023-01-01", None),
    )

    rows: list[dict[str, object]] = []

    for name, start, end in eras:
        mask = df["date"] >= pd.Timestamp(start)
        if end is not None:
            mask &= df["date"] <= pd.Timestamp(end)

        subset = df.loc[mask].dropna(subset=["composite_risk", "confidence_v1"])
        if subset.empty:
            continue

        rows.append(
            {
                "era": name,
                "start": subset["date"].min(),
                "end": subset["date"].max(),
                "observations": len(subset),
                "average_risk": float(subset["composite_risk"].mean()),
                "median_risk": float(subset["composite_risk"].median()),
                "average_confidence": float(subset["confidence_v1"].mean()),
                "high_risk_days_pct": float((subset["composite_risk"] >= 0.85).mean() * 100.0),
                "low_risk_days_pct": float((subset["composite_risk"] <= 0.40).mean() * 100.0),
            }
        )

    return pd.DataFrame(rows)
