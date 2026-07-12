"""Streamlit dashboard for OBRM v0.6.0."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from obrm.analytics.service import build_risk_dataset
from obrm.core.config import load_config
from obrm.core.features import FEATURES
from obrm.core.paths import BTC_PRICE_FILE
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.data.catalog import load_dataset_status
from obrm.data.engine import BTC_METADATA_FILE, MarketDataEngine
from obrm.research.backtest import BacktestConfig, compare_strategies
from obrm.research.diagnostics import action_summary

PRICE_COLOUR = "#5DADE2"
FAIR_VALUE_COLOUR = "#2ECC71"
RISK_COLOUR = "#FF9AA2"

def format_date(value: object) -> str:
    return pd.Timestamp(value).strftime("%d-%b-%Y")

@st.cache_data
def load_price_data() -> pd.DataFrame:
    return MarketDataEngine().get_btc_price_history()

@st.cache_data
def load_analytics() -> pd.DataFrame:
    return build_risk_dataset(load_price_data())

def build_market_chart(df: pd.DataFrame) -> go.Figure:
    plotted = df.dropna(subset=["fair_value_usd", "composite_risk", "confidence_v1"]).copy()
    customdata = list(zip(
        plotted["date"].dt.strftime("%d-%b-%Y"), plotted["fair_value_usd"], plotted["premium_pct"],
        plotted["price_position_risk"], plotted["momentum_risk"], plotted["volatility_risk"],
        plotted["composite_risk"], plotted["confidence_v1"], plotted["market_phase"],
        plotted["decision_label"], plotted["dca_in_multiplier"], plotted["dca_out_pct_weekly"],
        plotted["provider"],
    ))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=plotted["date"], y=plotted["price_usd"], mode="lines", name="BTC Price",
        line={"color": PRICE_COLOUR, "width": 1.5}, customdata=customdata,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br><br>BTC Price: $%{y:,.2f}<br>"
            "Fair Value: $%{customdata[1]:,.2f}<br>Premium / Discount: %{customdata[2]:+.1f}%<br><br>"
            "Valuation Risk: %{customdata[3]:.2f}<br>Momentum Risk: %{customdata[4]:.2f}<br>"
            "Volatility Risk: %{customdata[5]:.2f}<br>Composite Risk: %{customdata[6]:.2f}<br>"
            "Confidence v1: %{customdata[7]:.0%}<br>Market Phase: %{customdata[8]}<br>"
            "Decision: %{customdata[9]}<br>DCA In: %{customdata[10]:.2f}× normal<br>"
            "DCA Out: %{customdata[11]:.2f}% weekly<br>Source: %{customdata[12]}<extra></extra>"
        )), secondary_y=False)
    fig.add_trace(go.Scatter(x=plotted["date"], y=plotted["fair_value_usd"], mode="lines",
                             name="Log Regression Fair Value", line={"color": FAIR_VALUE_COLOUR, "width": 1.5}, hoverinfo="skip"), secondary_y=False)
    fig.add_trace(go.Scatter(x=plotted["date"], y=plotted["composite_risk"], mode="lines",
                             name="Composite OBRM Risk", line={"color": RISK_COLOUR, "width": 1.5}, hoverinfo="skip"), secondary_y=True)
    fig.update_yaxes(title_text="BTC Price (USD, log scale)", type="log", secondary_y=False)
    fig.update_yaxes(title_text="Composite Risk", range=[0, 1], secondary_y=True)
    fig.update_layout(title="Bitcoin Price, Fair Value, and Composite OBRM Risk", xaxis_title="Date",
                      hovermode="x unified", height=820, margin={"l": 70, "r": 55, "t": 120, "b": 60},
                      legend={"orientation": "h", "x": 0, "y": 1.08, "yanchor": "bottom"})
    return fig

def build_backtest_chart(fixed: pd.DataFrame, dynamic: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fixed["date"], y=fixed["wealth_usd"], mode="lines", name="Fixed DCA wealth"))
    fig.add_trace(go.Scatter(x=dynamic["date"], y=dynamic["wealth_usd"], mode="lines", name="OBRM dynamic wealth"))
    fig.update_layout(title="Historical Portfolio Wealth", xaxis_title="Date", yaxis_title="Portfolio wealth (USD)",
                      hovermode="x unified", height=620, legend={"orientation": "h", "y": 1.08, "yanchor": "bottom"})
    return fig

def build_allocation_chart(dynamic: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dynamic["date"], y=dynamic["btc_value_usd"], mode="lines", stackgroup="one", name="BTC value"))
    fig.add_trace(go.Scatter(x=dynamic["date"], y=dynamic["cash_usd"], mode="lines", stackgroup="one", name="Cash"))
    fig.update_layout(title="OBRM Dynamic Portfolio Allocation", xaxis_title="Date", yaxis_title="USD value",
                      hovermode="x unified", height=520, legend={"orientation": "h", "y": 1.08, "yanchor": "bottom"})
    return fig

def render_dashboard(df: pd.DataFrame) -> None:
    latest = df.dropna(subset=["composite_risk", "confidence_v1"]).iloc[-1]
    status = load_dataset_status(BTC_METADATA_FILE)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest BTC Price", f"${latest['price_usd']:,.0f}")
    c2.metric("Composite OBRM Risk", f"{latest['composite_risk']:.2f}")
    c3.metric("Confidence v1", f"{latest['confidence_v1']:.0%}")
    c4.metric("Market Phase", latest["market_phase"])
    st.warning("OBRM remains a research alpha. DCA-out guidance excludes fees, taxes, spread, and slippage.")
    st.plotly_chart(build_market_chart(df), width="stretch")
    st.subheader("Decision Engine preview")
    a, b, c, d = st.columns(4)
    a.metric("Suggested Action", latest["decision_label"])
    b.metric("DCA In", f"{latest['dca_in_multiplier']:.2f}× normal")
    c.metric("DCA Out", f"{latest['dca_out_pct_weekly']:.2f}% holdings/week")
    d.metric("Fair Value", f"${latest['fair_value_usd']:,.0f}")
    st.caption(latest["decision_explanation"])
    st.subheader("Risk components")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Valuation", f"{latest['price_position_risk']:.2f}")
    r2.metric("Momentum", f"{latest['momentum_risk']:.2f}")
    r3.metric("Volatility", f"{latest['volatility_risk']:.2f}")
    r4.metric("Agreement", f"{latest['component_agreement']:.0%}")
    health = "Unknown" if status is None else (f"Stale · {status.days_behind_utc} days" if status.is_stale else "Healthy")
    st.caption(f"Latest date: {format_date(latest['date'])} · Data health: {health} · Current point source: {latest['provider']}")

def render_backtesting_lab(df: pd.DataFrame) -> None:
    st.header("Backtesting Lab")
    st.warning("Research simulation only. Results exclude fees, taxes, spread, slippage, custody risk, and execution errors.")
    model_rows = df.dropna(subset=["composite_risk", "confidence_v1"])
    model_start = pd.Timestamp(model_rows["date"].min()).date()
    model_end = pd.Timestamp(model_rows["date"].max()).date()
    c1, c2, c3 = st.columns(3)
    weekly = c1.number_input("Weekly contribution (USD)", min_value=10.0, max_value=10000.0, value=100.0, step=10.0)
    start = c2.date_input("Start date", value=model_start, min_value=model_start, max_value=model_end)
    starting_cash = c3.number_input("Starting cash (USD)", min_value=0.0, max_value=1_000_000.0, value=0.0, step=100.0)
    config = BacktestConfig(float(weekly), float(starting_cash), str(start), str(model_end))
    fixed, dynamic, summary = compare_strategies(df, config)
    fixed_summary = summary.loc[summary["strategy"] == "fixed_dca"].iloc[0]
    dynamic_summary = summary.loc[summary["strategy"] == "obrm_dynamic"].iloc[0]
    st.subheader("Outcome comparison")
    x1, x2, x3, x4 = st.columns(4)
    x1.metric("Fixed DCA wealth", f"${fixed_summary['ending_wealth_usd']:,.0f}")
    x2.metric("OBRM dynamic wealth", f"${dynamic_summary['ending_wealth_usd']:,.0f}", delta=f"${dynamic_summary['ending_wealth_usd'] - fixed_summary['ending_wealth_usd']:,.0f}")
    x3.metric("Fixed max drawdown", f"{fixed_summary['max_drawdown_pct']:.1f}%")
    x4.metric("OBRM max drawdown", f"{dynamic_summary['max_drawdown_pct']:.1f}%", delta=f"{dynamic_summary['max_drawdown_pct'] - fixed_summary['max_drawdown_pct']:+.1f} pp", delta_color="inverse")
    st.plotly_chart(build_backtest_chart(fixed, dynamic), width="stretch")
    st.plotly_chart(build_allocation_chart(dynamic), width="stretch")
    st.subheader("Strategy summary")
    st.dataframe(summary[["strategy", "weeks", "contributed_usd", "ending_cash_usd", "ending_btc", "ending_wealth_usd", "return_on_contributions_pct", "max_drawdown_pct"]], width="stretch", hide_index=True)
    st.subheader("OBRM action diagnostics")
    st.dataframe(action_summary(dynamic), width="stretch", hide_index=True)

def render_research_console(df: pd.DataFrame) -> None:
    st.header("Research Console")
    status = load_dataset_status(BTC_METADATA_FILE)
    expected = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    missing = expected.difference(pd.DatetimeIndex(df["date"])).size
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Missing calendar days", f"{missing:,}")
    c3.metric("Coverage start", format_date(df["date"].min()))
    c4.metric("Coverage end", format_date(df["date"].max()))
    latest = df.dropna(subset=["composite_risk", "confidence_v1"]).iloc[-1]
    st.subheader("Composite model diagnostics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Composite Risk", f"{latest['composite_risk']:.3f}")
    m2.metric("Confidence v1", f"{latest['confidence_v1']:.0%}")
    m3.metric("Component Agreement", f"{latest['component_agreement']:.0%}")
    m4.metric("Component Coverage", f"{latest['component_coverage']:.0%}")
    st.dataframe(pd.DataFrame([
        {"Component": "Valuation", "Weight": "45%", "Latest": latest["price_position_risk"]},
        {"Component": "Momentum", "Weight": "30%", "Latest": latest["momentum_risk"]},
        {"Component": "Volatility", "Weight": "25%", "Latest": latest["volatility_risk"]},
    ]), width="stretch", hide_index=True)
    st.subheader("Feature Registry")
    st.dataframe([{"Feature": f.name, "Category": f.category, "Status": "Available" if f.available else "Planned", "Version": f.version_added} for f in FEATURES], width="stretch", hide_index=True)
    st.subheader("Dataset integrity")
    st.write(f"**Local file:** `{BTC_PRICE_FILE}`")
    if status is not None:
        st.write(f"**Downloaded:** {status.downloaded_at_utc}")
        st.write(f"**SHA-256:** `{status.sha256}`")

def main() -> None:
    st.set_page_config(page_title="OBRM Dashboard", page_icon="📈", layout="wide")
    config = load_config()
    st.title(APP_NAME)
    st.caption(f"Version {APP_VERSION}")
    page = st.sidebar.radio("Navigation", ("Dashboard", "Backtesting Lab", "Research Console"))
    if st.sidebar.button("Refresh market data"):
        MarketDataEngine(config).refresh_btc_price_history()
        st.cache_data.clear()
        st.rerun()
    st.sidebar.caption(f"Historical source: {config.primary_provider}\n\nLive source: Yahoo Finance\n\nDate format: DD-Mon-YYYY")
    df = load_analytics()
    if page == "Dashboard":
        render_dashboard(df)
    elif page == "Backtesting Lab":
        render_backtesting_lab(df)
    else:
        render_research_console(df)

if __name__ == "__main__":
    main()
