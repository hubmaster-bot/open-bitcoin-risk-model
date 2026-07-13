"""Validation for canonical research datasets."""

from __future__ import annotations

import pandas as pd


def validate_research_dataset(
    frame: pd.DataFrame,
    metrics: tuple[str, ...],
) -> None:
    """Validate the normalized canonical research-data schema."""
    required = {"date", "provider", "asset", *metrics}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing research-data columns: {sorted(missing)}")

    if frame.empty:
        raise ValueError("Research dataset is empty.")

    if frame["date"].isna().any():
        raise ValueError("Research dataset contains invalid dates.")

    if frame["date"].duplicated().any():
        raise ValueError("Research dataset contains duplicate dates.")

    if not frame["date"].is_monotonic_increasing:
        raise ValueError("Research dataset dates must be sorted.")

    if frame["provider"].isna().any() or frame["asset"].isna().any():
        raise ValueError("Provider and asset provenance must be present.")

    unavailable = [
        metric for metric in metrics if frame[metric].notna().sum() == 0
    ]
    if unavailable:
        raise ValueError(
            "Requested metrics contain no usable observations: "
            + ", ".join(unavailable)
        )


def missing_calendar_dates(frame: pd.DataFrame) -> int:
    """Count missing daily dates inside the observed coverage range."""
    expected = pd.date_range(
        frame["date"].min(),
        frame["date"].max(),
        freq="D",
    )
    return int(
        expected.difference(pd.DatetimeIndex(frame["date"])).size
    )
