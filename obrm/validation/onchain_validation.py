"""Validation of the provisional on-chain research layer."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from obrm.validation.buckets import bucket_forward_returns
from obrm.validation.correlation import (
    correlation_matrix,
    maximum_absolute_correlation,
)
from obrm.validation.forward_returns import (
    DEFAULT_HORIZONS,
    add_forward_returns,
)
from obrm.validation.readiness import (
    ReadinessAssessment,
    assess_readiness,
)


@dataclass(frozen=True)
class OnChainValidationReport:
    merged: pd.DataFrame
    bucket_summary: pd.DataFrame
    subdimension_bucket_summary: dict[str, pd.DataFrame]
    correlations: pd.DataFrame
    strongest_existing_correlation_name: str | None
    strongest_existing_correlation_value: float | None
    monotonicity_by_horizon: dict[int, float | None]
    incremental_comparison: pd.DataFrame
    readiness: ReadinessAssessment
    usable_start: str | None
    usable_end: str | None
    usable_rows: int
    total_rows: int


def merge_price_and_onchain(
    market_frame: pd.DataFrame,
    onchain_frame: pd.DataFrame,
) -> pd.DataFrame:
    """Merge validated on-chain evidence with the existing market model."""
    required_market = {
        "date",
        "price_usd",
        "price_position_risk",
        "momentum_risk",
        "volatility_risk",
        "composite_risk",
    }
    required_onchain = {
        "date",
        "realized_valuation_score",
        "network_strength_score",
        "onchain_research_score",
    }

    missing_market = required_market - set(market_frame.columns)
    missing_onchain = required_onchain - set(onchain_frame.columns)

    if missing_market:
        raise ValueError(
            "Market validation data is missing: "
            + ", ".join(sorted(missing_market))
        )
    if missing_onchain:
        raise ValueError(
            "On-chain validation data is missing: "
            + ", ".join(sorted(missing_onchain))
        )

    market = market_frame.copy()
    onchain = onchain_frame.copy()
    market["date"] = pd.to_datetime(market["date"]).dt.normalize()
    onchain["date"] = pd.to_datetime(onchain["date"]).dt.normalize()

    return (
        market.merge(
            onchain[
                [
                    "date",
                    "mvrv",
                    "hash_rate",
                    "realized_valuation_score",
                    "network_strength_score",
                    "onchain_research_score",
                    "onchain_input_coverage",
                ]
            ],
            on="date",
            how="left",
            validate="one_to_one",
        )
        .sort_values("date")
        .reset_index(drop=True)
    )


def monotonicity_ratio(
    bucket_summary: pd.DataFrame,
    return_mean_column: str,
) -> float | None:
    """Measure how often higher risk bands have lower future returns."""
    if return_mean_column not in bucket_summary.columns:
        return None

    values = pd.to_numeric(
        bucket_summary[return_mean_column],
        errors="coerce",
    ).dropna()

    if len(values) < 2:
        return None

    comparisons = [
        left >= right
        for left, right in zip(values.iloc[:-1], values.iloc[1:])
    ]
    return float(np.mean(comparisons)) if comparisons else None


def build_incremental_model(
    frame: pd.DataFrame,
    *,
    onchain_weight: float = 0.20,
) -> pd.DataFrame:
    """Create a provisional Composite Risk v2 for validation only."""
    if not 0.0 < onchain_weight < 1.0:
        raise ValueError("On-chain weight must be between 0 and 1.")

    df = frame.copy()
    existing_weight = 1.0 - onchain_weight
    df["composite_risk_v2_research"] = (
        existing_weight
        * pd.to_numeric(df["composite_risk"], errors="coerce")
        + onchain_weight
        * pd.to_numeric(
            df["onchain_research_score"],
            errors="coerce",
        )
    )
    return df


def compare_models(
    frame: pd.DataFrame,
    *,
    horizons: tuple[int, ...] = (90, 365, 730),
) -> pd.DataFrame:
    """Compare band ordering for Composite Risk v1 and research v2."""
    rows: list[dict[str, object]] = []

    for model_column, model_name in (
        ("composite_risk", "Composite Risk v1"),
        ("composite_risk_v2_research", "Research Composite v2"),
    ):
        return_columns = tuple(
            f"forward_return_{horizon}d"
            for horizon in horizons
        )
        summary = bucket_forward_returns(
            frame,
            score_column=model_column,
            return_columns=return_columns,
        )

        row: dict[str, object] = {"model": model_name}
        ratios: list[float] = []

        for horizon in horizons:
            column = f"{horizon}d_mean"
            ratio = monotonicity_ratio(summary, column)
            row[f"{horizon}d_monotonicity"] = ratio
            if ratio is not None:
                ratios.append(ratio)

        row["mean_monotonicity"] = (
            float(np.mean(ratios)) if ratios else None
        )
        rows.append(row)

    return pd.DataFrame(rows)


def build_onchain_validation_report(
    market_frame: pd.DataFrame,
    onchain_frame: pd.DataFrame,
    *,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    evidence_categories_available: int = 2,
    evidence_categories_intended: int = 4,
) -> OnChainValidationReport:
    """Build the complete v0.9.4 validation report."""
    merged = merge_price_and_onchain(market_frame, onchain_frame)
    labelled = add_forward_returns(
        merged,
        price_column="price_usd",
        horizons=horizons,
    )
    labelled = build_incremental_model(labelled)

    return_columns = tuple(
        f"forward_return_{horizon}d"
        for horizon in horizons
    )

    bucket_summary = bucket_forward_returns(
        labelled,
        score_column="onchain_research_score",
        return_columns=return_columns,
    )

    subdimension_bucket_summary = {
        "Realized Valuation": bucket_forward_returns(
            labelled,
            score_column="realized_valuation_score",
            return_columns=return_columns,
        ),
        "Network Strength": bucket_forward_returns(
            labelled,
            score_column="network_strength_score",
            return_columns=return_columns,
        ),
    }

    correlation_columns = (
        "onchain_research_score",
        "realized_valuation_score",
        "network_strength_score",
        "price_position_risk",
        "momentum_risk",
        "volatility_risk",
        "composite_risk",
    )
    correlations = correlation_matrix(
        labelled,
        correlation_columns,
    )

    strongest_name, strongest_value = maximum_absolute_correlation(
        correlations,
        "onchain_research_score",
        exclude=(
            "realized_valuation_score",
            "network_strength_score",
        ),
    )

    monotonicity_by_horizon = {
        horizon: monotonicity_ratio(
            bucket_summary,
            f"{horizon}d_mean",
        )
        for horizon in horizons
    }

    comparison = compare_models(
        labelled,
        horizons=tuple(
            horizon for horizon in horizons
            if horizon in {90, 365, 730}
        ),
    )

    usable_mask = labelled["onchain_research_score"].notna()
    usable_rows = int(usable_mask.sum())
    total_rows = int(len(labelled))
    valid_period_ratio = (
        usable_rows / total_rows if total_rows else 0.0
    )

    promotion_horizons = [
        monotonicity_by_horizon[horizon]
        for horizon in (90, 365, 730)
        if horizon in monotonicity_by_horizon
        and monotonicity_by_horizon[horizon] is not None
    ]
    overall_monotonicity = (
        float(np.mean(promotion_horizons))
        if promotion_horizons
        else None
    )

    readiness = assess_readiness(
        evidence_categories_available=evidence_categories_available,
        evidence_categories_intended=evidence_categories_intended,
        bucket_monotonicity_ratio=overall_monotonicity,
        maximum_existing_dimension_correlation=strongest_value,
        valid_period_ratio=valid_period_ratio,
    )

    usable_dates = labelled.loc[usable_mask, "date"]
    usable_start = (
        pd.Timestamp(usable_dates.min()).date().isoformat()
        if not usable_dates.empty
        else None
    )
    usable_end = (
        pd.Timestamp(usable_dates.max()).date().isoformat()
        if not usable_dates.empty
        else None
    )

    return OnChainValidationReport(
        merged=labelled,
        bucket_summary=bucket_summary,
        subdimension_bucket_summary=subdimension_bucket_summary,
        correlations=correlations,
        strongest_existing_correlation_name=strongest_name,
        strongest_existing_correlation_value=strongest_value,
        monotonicity_by_horizon=monotonicity_by_horizon,
        incremental_comparison=comparison,
        readiness=readiness,
        usable_start=usable_start,
        usable_end=usable_end,
        usable_rows=usable_rows,
        total_rows=total_rows,
    )
