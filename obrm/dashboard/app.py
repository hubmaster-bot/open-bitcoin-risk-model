"""Streamlit dashboard for OBRM v1.1.1."""
from dataclasses import replace
import math

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from obrm.analytics.explainability import build_dimension_snapshots
from obrm.analytics.service import build_risk_dataset
from obrm.core.config import load_config
from obrm.core.features import FEATURES
from obrm.core.paths import BTC_PRICE_FILE
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.data.catalog import load_dataset_status
from obrm.data.engine import BTC_METADATA_FILE, MarketDataEngine
from obrm.dashboard.annotations import (
    ChartAnnotation,
    annotations_csv,
    annotations_json,
    load_annotations,
    save_annotations,
)
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

def _format_price_tick(value: float) -> str:
    if value >= 1_000_000:
        return f"${value / 1_000_000:g}m"
    if value >= 1_000:
        return f"${value / 1_000:g}k"
    return f"${value:g}"


def _price_axis_ticks(values: pd.Series) -> tuple[list[float], list[str]]:
    positive = pd.to_numeric(values, errors="coerce").dropna()
    positive = positive[positive > 0]
    if positive.empty:
        return [], []
    minimum = float(positive.min())
    maximum = float(positive.max())
    lower_power = math.floor(math.log10(minimum))
    upper_power = math.ceil(math.log10(maximum))
    ticks = [
        multiplier * (10 ** power)
        for power in range(lower_power - 1, upper_power + 2)
        for multiplier in (1, 2, 5)
        if minimum * 0.5 <= multiplier * (10 ** power) <= maximum * 2.0
    ]
    return ticks, [_format_price_tick(value) for value in ticks]


def build_market_chart(
    df: pd.DataFrame, annotations: list[ChartAnnotation] | None = None
) -> go.Figure:
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
    fig.add_trace(go.Scatter(
        x=plotted["date"], y=plotted["fair_value_usd"], mode="lines",
        name="Log Regression Fair Value", line={"color": FAIR_VALUE_COLOUR, "width": 1.5},
        hoverinfo="skip"), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=plotted["date"], y=plotted["composite_risk"], mode="lines",
        name="Composite OBRM Risk", line={"color": RISK_COLOUR, "width": 1.5},
        hoverinfo="skip"), secondary_y=True)

    price_values = [plotted["price_usd"], plotted["fair_value_usd"]]
    visible_items = [item for item in (annotations or []) if item.visible]
    price_annotations = [float(item.value) for item in visible_items if item.kind == "horizontal_price"]
    if price_annotations:
        price_values.append(pd.Series(price_annotations))

    annotation_style = {
        "showarrow": False,
        "bgcolor": "rgba(15, 18, 24, 0.86)",
        "bordercolor": "rgba(255,255,255,0.25)",
        "borderpad": 3,
        "font": {"size": 11},
    }
    for item in visible_items:
        label = item.label or {
            "vertical_date": "Marked date",
            "horizontal_price": "Price level",
            "horizontal_risk": "Risk level",
        }[item.kind]
        line = {"dash": item.dash, "width": 1.2}
        if item.kind == "vertical_date":
            date_value = pd.Timestamp(str(item.value))
            fig.add_shape(type="line", x0=date_value, x1=date_value, y0=0, y1=1,
                          xref="x", yref="paper", line=line)
            fig.add_annotation(x=date_value, y=0.99, xref="x", yref="paper", text=label,
                               xanchor="left", yanchor="top", **annotation_style)
        elif item.kind == "horizontal_price":
            value = float(item.value)
            fig.add_shape(type="line", x0=0, x1=1, y0=value, y1=value,
                          xref="paper", yref="y", line=line)
            fig.add_annotation(x=0.995, y=value, xref="paper", yref="y",
                               text=f"{label}: ${value:,.0f}", xanchor="right",
                               yanchor="bottom", **annotation_style)
        else:
            value = float(item.value)
            fig.add_shape(type="line", x0=0, x1=1, y0=value, y1=value,
                          xref="paper", yref="y2", line=line)
            fig.add_annotation(x=0.995, y=value, xref="paper", yref="y2",
                               text=f"{label}: {value:.2f}", xanchor="right",
                               yanchor="bottom", **annotation_style)

    tick_values, tick_text = _price_axis_ticks(pd.concat(price_values, ignore_index=True))
    fig.update_yaxes(
        title_text="BTC Price (USD, log scale)", type="log", secondary_y=False,
        tickmode="array", tickvals=tick_values, ticktext=tick_text, automargin=True,
    )
    fig.update_yaxes(title_text="Composite Risk", range=[0, 1], secondary_y=True, automargin=True)
    fig.update_layout(
        title={"text": "Bitcoin Price, Fair Value, and Composite OBRM Risk", "x": 0, "y": 0.985},
        xaxis_title="Date", hovermode="x unified", height=820,
        margin={"l": 82, "r": 72, "t": 145, "b": 60},
        legend={"orientation": "h", "x": 0, "y": 1.035, "yanchor": "bottom"},
    )
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

def _annotation_state() -> list[ChartAnnotation]:
    if "chart_annotations" not in st.session_state:
        st.session_state.chart_annotations = load_annotations()
    return st.session_state.chart_annotations


def _persist_annotation_state(items: list[ChartAnnotation]) -> None:
    st.session_state.chart_annotations = items
    save_annotations(items)


def _render_research_inspector(df: pd.DataFrame) -> None:
    valid = df.dropna(subset=["composite_risk", "confidence_v1"]).copy()
    minimum = pd.Timestamp(valid["date"].min()).date()
    maximum = pd.Timestamp(valid["date"].max()).date()
    selected = st.date_input(
        "Inspect date", value=maximum, min_value=minimum, max_value=maximum, key="inspect_date"
    )
    distances = (valid["date"] - pd.Timestamp(selected)).abs()
    row = valid.loc[distances.idxmin()]
    st.caption(f"Nearest observation: {format_date(row['date'])}")
    st.metric("Composite Risk", f"{row['composite_risk']:.3f}")
    st.metric("BTC Price", f"${row['price_usd']:,.0f}")
    st.metric("Market Phase", str(row["market_phase"]))
    st.metric("Confidence", f"{row['confidence_v1']:.0%}")
    snapshots = build_dimension_snapshots(row)
    st.markdown("**Contributors**")
    for item in snapshots:
        st.progress(min(max(item.score, 0.0), 1.0), text=f"{item.display_name}: {item.score:.2f}")
        st.caption(f"{item.weight:.0%} weight · contribution {item.contribution:.3f}")
        with st.expander(f"Why {item.display_name.lower()} is {item.label.lower()}"):
            st.write(item.explanation)
    st.caption(f"Decision: {row['decision_label']} · Source: {row['provider']}")


def _render_chart_tools(df: pd.DataFrame) -> None:
    items = _annotation_state()
    type_label = st.selectbox("Line type", ["Date", "Price", "Risk"], key="annotation_type")
    kind = {"Date": "vertical_date", "Price": "horizontal_price", "Risk": "horizontal_risk"}[type_label]
    if kind == "vertical_date":
        value = st.date_input(
            "Date", value=pd.Timestamp(df["date"].max()).date(), key="annotation_date"
        )
    elif kind == "horizontal_price":
        value = st.number_input("Price (USD)", min_value=1.0, value=100000.0, step=1000.0)
    else:
        value = st.number_input("Risk level", min_value=0.0, max_value=1.0, value=0.50, step=0.05)
    label = st.text_input("Label", placeholder="e.g. Cycle top, entry, caution")
    dash = st.selectbox("Style", ["dash", "dot", "solid", "longdash"])
    if st.button("Add line", type="primary", use_container_width=True):
        created = ChartAnnotation.create(kind, value, label, dash)
        _persist_annotation_state([*items, created])
        st.rerun()

    st.markdown("**Saved lines**")
    if not items:
        st.caption("No annotations saved yet.")
    for item in items:
        label_text = item.label or item.kind.replace("_", " ").title()
        c1, c2, c3 = st.columns([4, 1.4, 0.8])
        c1.caption(f"{label_text} · {item.value}")
        visible = c2.toggle("Show", value=item.visible, key=f"visible-{item.id}")
        if visible != item.visible:
            updated = [replace(candidate, visible=visible) if candidate.id == item.id else candidate for candidate in items]
            _persist_annotation_state(updated)
            st.rerun()
        if c3.button("×", key=f"delete-{item.id}", help="Delete annotation"):
            _persist_annotation_state([candidate for candidate in items if candidate.id != item.id])
            st.rerun()
    if items:
        st.download_button(
            "Export JSON", annotations_json(items), "obrm-chart-annotations.json", "application/json",
            use_container_width=True,
        )
        st.download_button(
            "Export CSV", annotations_csv(items), "obrm-chart-annotations.csv", "text/csv",
            use_container_width=True,
        )
        if st.button("Clear all lines", use_container_width=True):
            _persist_annotation_state([])
            st.rerun()


def render_dashboard(df: pd.DataFrame) -> None:
    latest = df.dropna(subset=["composite_risk", "confidence_v1"]).iloc[-1]
    status = load_dataset_status(BTC_METADATA_FILE)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest BTC Price", f"${latest['price_usd']:,.0f}")
    c2.metric("Composite OBRM Risk", f"{latest['composite_risk']:.2f}")
    c3.metric("Confidence v1", f"{latest['confidence_v1']:.0%}")
    c4.metric("Market Phase", latest["market_phase"])
    st.warning("OBRM is research software. DCA-out guidance excludes fees, taxes, spread, and slippage.")
    chart_column, inspector_column = st.columns([3.4, 1.25], gap="large")
    with chart_column:
        st.plotly_chart(build_market_chart(df, _annotation_state()), width="stretch", config={"scrollZoom": True})
    with inspector_column:
        inspector_tab, tools_tab = st.tabs(["Research Inspector", "Chart Tools"])
        with inspector_tab:
            _render_research_inspector(df)
        with tools_tab:
            _render_chart_tools(df)
    st.subheader("Decision Engine preview")
    a, b, c, d = st.columns(4)
    a.metric("Suggested Action", latest["decision_label"])
    b.metric("DCA In", f"{latest['dca_in_multiplier']:.2f}× normal")
    c.metric("DCA Out", f"{latest['dca_out_pct_weekly']:.2f}% holdings/week")
    d.metric("Fair Value", f"${latest['fair_value_usd']:,.0f}")
    st.caption(latest["decision_explanation"])
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
