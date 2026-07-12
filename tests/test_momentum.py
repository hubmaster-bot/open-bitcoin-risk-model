"""Tests for momentum risk."""

import numpy as np
import pandas as pd

from obrm.analytics.momentum import calculate_momentum_risk


def test_momentum_risk_is_bounded() -> None:
    dates = pd.date_range("2020-01-01", periods=600, freq="D")
    prices = 100 * np.exp(np.linspace(0, 2, len(dates)))
    df = pd.DataFrame({"date": dates, "price_usd": prices})

    result = calculate_momentum_risk(df)
    risk = result["momentum_risk"].dropna()

    assert not risk.empty
    assert risk.between(0.0, 1.0).all()
