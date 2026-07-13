"""Tests for canonical research-data validation."""

import pandas as pd
import pytest

from obrm.research_data.validation import (
    missing_calendar_dates,
    validate_research_dataset,
)


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "MetricA": [1.0, 2.0],
            "provider": ["Test", "Test"],
            "asset": ["btc", "btc"],
        }
    )


def test_valid_research_dataset_passes() -> None:
    validate_research_dataset(_frame(), ("MetricA",))


def test_unavailable_metric_is_rejected() -> None:
    frame = _frame()
    frame["MetricA"] = pd.NA

    with pytest.raises(ValueError, match="no usable observations"):
        validate_research_dataset(frame, ("MetricA",))


def test_missing_calendar_dates_are_counted() -> None:
    frame = _frame().iloc[[0]].copy()
    frame.loc[frame.index[0], "date"] = pd.Timestamp("2026-01-01")
    extra = frame.copy()
    extra["date"] = pd.Timestamp("2026-01-03")
    combined = pd.concat([frame, extra], ignore_index=True)

    assert missing_calendar_dates(combined) == 1
