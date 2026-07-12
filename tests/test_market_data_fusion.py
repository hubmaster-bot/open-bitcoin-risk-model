"""Tests for market data fusion and provenance."""

import pandas as pd

from obrm.data.merge import merge_price_history, source_segments


def _frame(dates: list[str], prices: list[float], provider: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(dates),
            "price_usd": prices,
            "provider": [provider] * len(dates),
        }
    )


def test_live_data_wins_on_overlap() -> None:
    historical = _frame(
        ["2026-01-01", "2026-01-02"],
        [100.0, 101.0],
        "Historical",
    )
    live = _frame(
        ["2026-01-02", "2026-01-03"],
        [201.0, 202.0],
        "Live",
    )

    merged = merge_price_history(historical, live)

    assert len(merged) == 3
    overlap = merged.loc[merged["date"] == pd.Timestamp("2026-01-02")].iloc[0]
    assert overlap["price_usd"] == 201.0
    assert overlap["provider"] == "Live"


def test_source_segments_describe_contiguous_provider_ranges() -> None:
    df = _frame(
        ["2026-01-01", "2026-01-02"],
        [100.0, 101.0],
        "Historical",
    )
    df = pd.concat(
        [
            df,
            _frame(
                ["2026-01-03", "2026-01-04"],
                [102.0, 103.0],
                "Live",
            ),
        ],
        ignore_index=True,
    )

    segments = source_segments(df)

    assert len(segments) == 2
    assert segments[0].provider == "Historical"
    assert segments[0].start_date == "2026-01-01"
    assert segments[0].end_date == "2026-01-02"
    assert segments[1].provider == "Live"
