"""Tests for the OBRM backtesting engine."""
import pandas as pd
import pytest
from obrm.research.backtest import BacktestConfig, compare_strategies

def _analytics() -> pd.DataFrame:
    dates = pd.date_range("2020-01-01", periods=900, freq="D")
    return pd.DataFrame({
        "date": dates,
        "price_usd": pd.Series(range(100, 1000), dtype=float),
        "composite_risk": 0.30,
        "confidence_v1": 0.90,
        "decision_action": "dca_in",
        "decision_label": "Accumulation",
        "dca_in_multiplier": 1.75,
        "dca_out_pct_weekly": 0.0,
    })

def test_strategies_use_equal_external_contributions() -> None:
    fixed, dynamic, summary = compare_strategies(_analytics(), BacktestConfig(weekly_contribution_usd=100.0))
    assert len(fixed) == len(dynamic)
    assert summary["contributed_usd"].nunique() == 1

def test_dynamic_strategy_never_spends_more_cash_than_available() -> None:
    _, dynamic, _ = compare_strategies(_analytics(), BacktestConfig(weekly_contribution_usd=100.0))
    assert (dynamic["cash_usd"] >= -1e-9).all()

def test_invalid_weekly_contribution_is_rejected() -> None:
    with pytest.raises(ValueError, match="positive"):
        compare_strategies(_analytics(), BacktestConfig(weekly_contribution_usd=0.0))
