"""Merge historical and live market datasets."""

from dataclasses import dataclass

import pandas as pd

from obrm.data.validator import validate_price_data


@dataclass(frozen=True)
class SourceSegment:
    """A contiguous date range supplied by one provider."""

    provider: str
    start_date: str
    end_date: str
    rows: int


def merge_price_history(
    historical: pd.DataFrame,
    live: pd.DataFrame,
) -> pd.DataFrame:
    """Merge standardized datasets, preferring live data on overlapping dates."""
    historical_copy = historical.copy()
    live_copy = live.copy()

    historical_copy["_priority"] = 0
    live_copy["_priority"] = 1

    merged = pd.concat(
        [historical_copy, live_copy],
        ignore_index=True,
    )

    merged = (
        merged.sort_values(["date", "_priority"])
        .drop_duplicates(subset="date", keep="last")
        .drop(columns="_priority")
        .sort_values("date")
        .reset_index(drop=True)
    )

    validate_price_data(merged)
    return merged


def source_segments(df: pd.DataFrame) -> tuple[SourceSegment, ...]:
    """Summarize contiguous provider segments in a merged dataset."""
    validate_price_data(df)

    working = df[["date", "provider"]].copy()
    working["group"] = working["provider"].ne(
        working["provider"].shift()
    ).cumsum()

    segments: list[SourceSegment] = []
    for _, group in working.groupby("group", sort=True):
        segments.append(
            SourceSegment(
                provider=str(group["provider"].iloc[0]),
                start_date=pd.Timestamp(group["date"].min()).date().isoformat(),
                end_date=pd.Timestamp(group["date"].max()).date().isoformat(),
                rows=len(group),
            )
        )

    return tuple(segments)
