"""Tests for DCA-out behaviour."""
import pandas as pd
from obrm.research.backtest import BacktestConfig, compare_strategies

def test_dca_out_generates_sales_after_accumulation() -> None:
    dates = pd.date_range("2020-01-01", periods=1000, freq="D")
    half = len(dates) // 2
    df = pd.DataFrame({
        "date": dates,
        "price_usd": [100.0 + i for i in range(len(dates))],
        "composite_risk": [0.30] * half + [0.90] * (len(dates) - half),
        "confidence_v1": 0.90,
        "decision_action": ["dca_in"] * half + ["dca_out"] * (len(dates) - half),
        "decision_label": ["Accumulation"] * half + ["Gradual DCA out"] * (len(dates) - half),
        "dca_in_multiplier": [1.75] * half + [0.0] * (len(dates) - half),
        "dca_out_pct_weekly": [0.0] * half + [0.5] * (len(dates) - half),
    })
    _, dynamic, _ = compare_strategies(df, BacktestConfig(weekly_contribution_usd=100.0))
    assert dynamic["sell_btc"].sum() > 0
    assert dynamic.iloc[-1]["cash_usd"] > 0
