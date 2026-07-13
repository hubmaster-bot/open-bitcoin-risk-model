"""Tests for forward-return labels."""

import pandas as pd
import pytest

from obrm.validation.forward_returns import add_forward_returns


def test_forward_returns_use_future_prices_only_as_labels() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=4, freq="D"),
            "price_usd": [100.0, 110.0, 121.0, 133.1],
        }
    )

    result = add_forward_returns(frame, horizons=(1, 2))

    assert result.loc[0, "forward_return_1d"] == pytest.approx(0.10)
    assert result.loc[0, "forward_return_2d"] == pytest.approx(0.21)
    assert pd.isna(result.loc[3, "forward_return_1d"])
