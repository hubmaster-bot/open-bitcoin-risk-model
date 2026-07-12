"""Tests for volatility risk."""

import numpy as np
import pandas as pd

from obrm.analytics.volatility import calculate_volatility_risk


def test_volatility_risk_is_bounded() -> None:
    dates = pd.date_range("2020-01-01", periods=700, freq="D")
    prices = 100 * np.exp(np.linspace(0, 1, len(dates)))
    df = pd.DataFrame({"date": dates, "price_usd": prices})

    result = calculate_volatility_risk(df)
    risk = result["volatility_risk"].dropna()

    assert not risk.empty
    assert risk.between(0.0, 1.0).all()
