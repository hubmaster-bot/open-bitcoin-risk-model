"""Tests for the Market Data Engine."""

import pandas as pd
import pytest

from obrm.data.validator import validate_price_data


def test_valid_standardized_price_data() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "price_usd": [90000.0, 91000.0],
            "provider": ["Test", "Test"],
        }
    )
    validate_price_data(df)


def test_duplicate_dates_are_rejected() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-01"]),
            "price_usd": [90000.0, 91000.0],
            "provider": ["Test", "Test"],
        }
    )

    with pytest.raises(ValueError, match="duplicate dates"):
        validate_price_data(df)
