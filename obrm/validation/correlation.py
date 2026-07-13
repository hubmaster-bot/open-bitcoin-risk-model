"""Correlation and redundancy diagnostics."""

from __future__ import annotations

import pandas as pd


def correlation_matrix(
    frame: pd.DataFrame,
    columns: tuple[str, ...],
) -> pd.DataFrame:
    """Return a Pearson correlation matrix for selected columns."""
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(
            "Correlation analysis is missing columns: "
            + ", ".join(sorted(missing))
        )

    numeric = frame[list(columns)].apply(
        pd.to_numeric,
        errors="coerce",
    )
    return numeric.corr(method="pearson")


def maximum_absolute_correlation(
    matrix: pd.DataFrame,
    target: str,
    *,
    exclude: tuple[str, ...] = (),
) -> tuple[str | None, float | None]:
    """Return the strongest absolute correlation for one target."""
    if target not in matrix.index:
        raise ValueError(f"Target not found in correlation matrix: {target}")

    series = matrix.loc[target].drop(
        labels=[target, *exclude],
        errors="ignore",
    ).dropna()

    if series.empty:
        return None, None

    strongest = series.abs().idxmax()
    return str(strongest), float(series.loc[strongest])
