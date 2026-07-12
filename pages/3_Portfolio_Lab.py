"""Personal portfolio planning page for OBRM."""

import pandas as pd
import streamlit as st

from obrm.analytics.service import build_risk_dataset
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.data.engine import MarketDataEngine
from obrm.portfolio.model import (
    PortfolioInputs,
    portfolio_recommendation,
    portfolio_snapshot,
)


st.set_page_config(
    page_title="OBRM Portfolio Lab",
    page_icon="💼",
    layout="wide",
)


@st.cache_data
def load_portfolio_context() -> pd.DataFrame:
    prices = MarketDataEngine().get_btc_price_history()
    return build_risk_dataset(prices)


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Portfolio Lab")

st.warning(
    "This is portfolio-planning research, not personal financial advice. "
    "Tax, fees, liquidity needs, debt, income stability, and legal circumstances "
    "are not included."
)

analytics = load_portfolio_context()
latest = analytics.dropna(
    subset=["composite_risk", "confidence_v1"]
).iloc[-1]

st.subheader("Your portfolio inputs")
c1, c2, c3 = st.columns(3)
btc_holdings = c1.number_input(
    "BTC holdings",
    min_value=0.0,
    value=1.0,
    step=0.01,
    format="%.8f",
)
cash_available = c2.number_input(
    "Cash available (USD)",
    min_value=0.0,
    value=10000.0,
    step=100.0,
)
normal_weekly_dca = c3.number_input(
    "Normal weekly DCA (USD)",
    min_value=0.0,
    value=100.0,
    step=10.0,
)

c4, c5, c6 = st.columns(3)
total_contributed = c4.number_input(
    "Total capital contributed (USD)",
    min_value=0.0,
    value=50000.0,
    step=500.0,
)
target_allocation = c5.slider(
    "Target BTC allocation",
    min_value=0,
    max_value=100,
    value=80,
    step=5,
)
permanent_core = c6.slider(
    "Permanent BTC core",
    min_value=0,
    max_value=100,
    value=70,
    step=5,
)

capital_recovery = st.checkbox(
    "Limit DCA-out sales to unrecovered contributed capital",
    value=False,
)

inputs = PortfolioInputs(
    btc_holdings=float(btc_holdings),
    cash_available_usd=float(cash_available),
    normal_weekly_dca_usd=float(normal_weekly_dca),
    total_contributed_usd=float(total_contributed),
    permanent_core_btc_pct=float(permanent_core),
    target_btc_allocation_pct=float(target_allocation),
    capital_recovery_enabled=capital_recovery,
)

snapshot = portfolio_snapshot(inputs, float(latest["price_usd"]))
recommendation = portfolio_recommendation(
    inputs=inputs,
    snapshot=snapshot,
    decision_action=str(latest["decision_action"]),
    decision_label=str(latest["decision_label"]),
    dca_in_multiplier=float(latest["dca_in_multiplier"]),
    dca_out_pct_weekly=float(latest["dca_out_pct_weekly"]),
    confidence=float(latest["confidence_v1"]),
)

st.subheader("Current portfolio")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Portfolio value", f"${snapshot.total_value_usd:,.0f}")
m2.metric("BTC value", f"${snapshot.btc_value_usd:,.0f}")
m3.metric("Cash", f"${snapshot.cash_value_usd:,.0f}")
m4.metric("BTC allocation", f"{snapshot.btc_allocation_pct:.1f}%")

m5, m6, m7, m8 = st.columns(4)
m5.metric("BTC price", f"${snapshot.btc_price_usd:,.0f}")
m6.metric("Unrealised gain/loss", f"${snapshot.unrealised_gain_usd:,.0f}")
m7.metric("Permanent core floor", f"{snapshot.core_btc_floor:.8f} BTC")
m8.metric("Unrecovered capital", f"${snapshot.unrecovered_capital_usd:,.0f}")

st.subheader("Portfolio-aware recommendation")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Action", recommendation.headline)
r2.metric("Buy this week", f"${recommendation.weekly_buy_usd:,.0f}")
r3.metric("Sell this week", f"{recommendation.weekly_sell_btc:.8f} BTC")
r4.metric("Sale value", f"${recommendation.weekly_sell_usd:,.0f}")

st.info(recommendation.explanation)

st.subheader("Projected position after one action")
p1, p2 = st.columns(2)
p1.metric(
    "Projected BTC holdings",
    f"{recommendation.projected_btc_after_action:.8f} BTC",
)
p2.metric(
    "Projected cash",
    f"${recommendation.projected_cash_after_action:,.0f}",
)

st.subheader("Model context")
context1, context2, context3, context4 = st.columns(4)
context1.metric("Composite risk", f"{latest['composite_risk']:.2f}")
context2.metric("Confidence", f"{latest['confidence_v1']:.0%}")
context3.metric("Market phase", latest["market_phase"])
context4.metric("Generic decision", latest["decision_label"])

with st.expander("How the portfolio layer changes the generic decision"):
    st.markdown(
        """
        The Decision Engine first produces a generic action from market risk.

        The Portfolio Layer then applies personal constraints:

        - available cash,
        - current BTC allocation,
        - target allocation,
        - normal weekly DCA,
        - permanent core holdings, and
        - optional capital-recovery limits.

        It does **not** currently model tax, fees, debt, income, emergency funds,
        jurisdiction, or personal risk tolerance.
        """
    )
