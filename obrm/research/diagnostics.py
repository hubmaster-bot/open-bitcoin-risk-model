"""Backtest diagnostics."""
import pandas as pd

def action_summary(dynamic_results: pd.DataFrame) -> pd.DataFrame:
    return (dynamic_results.groupby("action", dropna=False)
            .agg(weeks=("date", "count"), total_buys_usd=("buy_usd", "sum"), total_btc_sold=("sell_btc", "sum"), average_risk=("composite_risk", "mean"), average_confidence=("confidence_v1", "mean"))
            .reset_index().sort_values("weeks", ascending=False))
