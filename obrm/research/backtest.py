"""Historical strategy simulator for OBRM."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class BacktestConfig:
    weekly_contribution_usd: float = 100.0
    starting_cash_usd: float = 0.0
    start_date: str | None = None
    end_date: str | None = None
    rebalance_frequency: str = "W-SUN"

@dataclass(frozen=True)
class BacktestSummary:
    strategy: str
    start_date: str
    end_date: str
    weeks: int
    contributed_usd: float
    ending_cash_usd: float
    ending_btc: float
    ending_btc_value_usd: float
    ending_wealth_usd: float
    gain_on_contributions_usd: float
    return_on_contributions_pct: float
    max_drawdown_pct: float

def _validate_config(config: BacktestConfig) -> None:
    if config.weekly_contribution_usd <= 0:
        raise ValueError("Weekly contribution must be positive.")
    if config.starting_cash_usd < 0:
        raise ValueError("Starting cash cannot be negative.")

def prepare_weekly_signals(analytics: pd.DataFrame, config: BacktestConfig) -> pd.DataFrame:
    required = {"date", "price_usd", "composite_risk", "confidence_v1", "decision_action", "decision_label", "dca_in_multiplier", "dca_out_pct_weekly"}
    missing = required - set(analytics.columns)
    if missing:
        raise ValueError(f"Missing backtest columns: {sorted(missing)}")
    df = analytics.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").set_index("date")
    if config.start_date:
        df = df.loc[pd.Timestamp(config.start_date):]
    if config.end_date:
        df = df.loc[:pd.Timestamp(config.end_date)]
    weekly = df.resample(config.rebalance_frequency).last().dropna(subset=["price_usd", "composite_risk", "confidence_v1"]).reset_index()
    if weekly.empty:
        raise ValueError("Backtest has no usable weekly observations.")
    return weekly

def _portfolio_drawdown(wealth: pd.Series) -> pd.Series:
    peak = wealth.cummax()
    return (wealth / peak.replace(0.0, np.nan)) - 1.0

def simulate_strategy(weekly: pd.DataFrame, config: BacktestConfig, strategy: str) -> tuple[pd.DataFrame, BacktestSummary]:
    if strategy not in {"fixed_dca", "obrm_dynamic"}:
        raise ValueError("Strategy must be 'fixed_dca' or 'obrm_dynamic'.")
    _validate_config(config)
    cash = float(config.starting_cash_usd)
    btc = 0.0
    contributed = 0.0
    rows: list[dict] = []
    for row in weekly.itertuples(index=False):
        price = float(row.price_usd)
        cash += config.weekly_contribution_usd
        contributed += config.weekly_contribution_usd
        buy_usd = 0.0
        sell_btc = 0.0
        action = "Fixed DCA" if strategy == "fixed_dca" else str(row.decision_label)
        if strategy == "fixed_dca":
            buy_usd = min(cash, config.weekly_contribution_usd)
        elif row.decision_action == "dca_in":
            buy_usd = min(cash, config.weekly_contribution_usd * float(row.dca_in_multiplier))
        elif row.decision_action == "dca_out":
            sell_btc = btc * (float(row.dca_out_pct_weekly) / 100.0)
        if buy_usd > 0:
            btc += buy_usd / price
            cash -= buy_usd
        if sell_btc > 0:
            btc -= sell_btc
            cash += sell_btc * price
        btc_value = btc * price
        wealth = cash + btc_value
        rows.append({"date": row.date, "price_usd": price, "composite_risk": float(row.composite_risk), "confidence_v1": float(row.confidence_v1), "action": action, "contribution_usd": config.weekly_contribution_usd, "buy_usd": buy_usd, "sell_btc": sell_btc, "cash_usd": cash, "btc_held": btc, "btc_value_usd": btc_value, "wealth_usd": wealth})
    result = pd.DataFrame(rows)
    result["drawdown"] = _portfolio_drawdown(result["wealth_usd"])
    latest = result.iloc[-1]
    capital = contributed + config.starting_cash_usd
    gain = float(latest["wealth_usd"]) - capital
    return_pct = gain / capital * 100.0 if capital > 0 else float("nan")
    summary = BacktestSummary(strategy, pd.Timestamp(result["date"].min()).strftime("%Y-%m-%d"), pd.Timestamp(result["date"].max()).strftime("%Y-%m-%d"), len(result), contributed, float(latest["cash_usd"]), float(latest["btc_held"]), float(latest["btc_value_usd"]), float(latest["wealth_usd"]), gain, return_pct, float(result["drawdown"].min() * 100.0))
    return result, summary

def compare_strategies(analytics: pd.DataFrame, config: BacktestConfig | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cfg = config or BacktestConfig()
    weekly = prepare_weekly_signals(analytics, cfg)
    fixed, fixed_summary = simulate_strategy(weekly, cfg, "fixed_dca")
    dynamic, dynamic_summary = simulate_strategy(weekly, cfg, "obrm_dynamic")
    return fixed, dynamic, pd.DataFrame([fixed_summary.__dict__, dynamic_summary.__dict__])
