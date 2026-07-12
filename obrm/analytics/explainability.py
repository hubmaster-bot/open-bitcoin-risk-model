"""Shared explainability helpers for OBRM."""

from dataclasses import dataclass
import pandas as pd

from obrm.analytics.dimensions import MARKET_DIMENSIONS, explain_dimension, score_label


@dataclass(frozen=True)
class DimensionSnapshot:
    key: str
    display_name: str
    score: float
    label: str
    weight: float
    contribution: float
    explanation: str


def _optional_float(row: pd.Series, column: str) -> float | None:
    if column not in row.index or pd.isna(row[column]):
        return None
    return float(row[column])


def build_dimension_snapshots(row: pd.Series) -> tuple[DimensionSnapshot, ...]:
    snapshots: list[DimensionSnapshot] = []
    for dimension in MARKET_DIMENSIONS:
        score = float(row[dimension.score_column])
        snapshots.append(
            DimensionSnapshot(
                key=dimension.key,
                display_name=dimension.display_name,
                score=score,
                label=score_label(score),
                weight=dimension.weight,
                contribution=score * dimension.weight,
                explanation=explain_dimension(
                    dimension.key,
                    score,
                    premium_pct=_optional_float(row, "premium_pct"),
                    return_30d=_optional_float(row, "return_30d"),
                    return_90d=_optional_float(row, "return_90d"),
                    realised_volatility_30d=_optional_float(row, "realised_volatility_30d"),
                    drawdown_from_ath=_optional_float(row, "drawdown_from_ath"),
                ),
            )
        )
    return tuple(snapshots)
