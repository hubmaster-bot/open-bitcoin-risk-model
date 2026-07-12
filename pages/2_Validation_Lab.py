"""Streamlit page for OBRM walk-forward validation."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from obrm.analytics.service import build_risk_dataset
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.data.engine import MarketDataEngine
from obrm.research.validation import (
    ValidationConfig,
    calibration_table,
    cycle_summary,
    forward_return_summary,
    monotonicity_score,
)


st.set_page_config(
    page_title="OBRM Validation Lab",
    page_icon="🧪",
    layout="wide",
)


@st.cache_data
def load_validation_data() -> pd.DataFrame:
    prices = MarketDataEngine().get_btc_price_history()
    return build_risk_dataset(prices)


def build_forward_return_chart(
    summary: pd.DataFrame,
    horizon_days: int,
) -> go.Figure:
    subset = summary.loc[summary["horizon_days"] == horizon_days].copy()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=subset["risk_band"],
            y=subset["median_return_pct"],
            name=f"{horizon_days}-day median return",
            customdata=subset[["observations", "positive_outcomes_pct"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Median return: %{y:.1f}%<br>"
                "Observations: %{customdata[0]}<br>"
                "Positive outcomes: %{customdata[1]:.1f}%"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=f"Median {horizon_days}-Day Forward Return by Risk Band",
        xaxis_title="Historical OBRM risk band",
        yaxis_title="Median forward return (%)",
        height=540,
    )
    return fig


def build_calibration_chart(table: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=table["validation_risk_band"].astype(str),
            y=table["negative_365d_outcomes_pct"],
            customdata=table[["observations", "average_risk"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Negative 365-day outcomes: %{y:.1f}%<br>"
                "Observations: %{customdata[0]}<br>"
                "Average risk: %{customdata[1]:.2f}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Observed Frequency of Negative 365-Day Outcomes",
        xaxis_title="Historical OBRM risk band",
        yaxis_title="Negative outcomes (%)",
        height=520,
    )
    return fig


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Validation Lab")

st.warning(
    "This page uses future returns only as outcome labels for historical "
    "validation. Future returns are never used to calculate the risk score."
)

analytics = load_validation_data()
model_rows = analytics.dropna(
    subset=["composite_risk", "confidence_v1"]
).copy()

control1, control2 = st.columns(2)
minimum_confidence = control1.slider(
    "Minimum confidence included",
    min_value=0.0,
    max_value=1.0,
    value=0.55,
    step=0.05,
)
horizon = control2.selectbox(
    "Primary forward-return horizon",
    options=[90, 365, 730],
    index=1,
    format_func=lambda value: f"{value} days",
)

config = ValidationConfig(minimum_confidence=minimum_confidence)
summary = forward_return_summary(model_rows, config)
calibration = calibration_table(model_rows, config)
cycles = cycle_summary(model_rows)
score = monotonicity_score(summary, horizon)

st.subheader("Headline validation")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Model observations", f"{len(model_rows):,}")
m2.metric("Validation start", model_rows["date"].min().strftime("%d-%b-%Y"))
m3.metric("Selected horizon", f"{horizon} days")
m4.metric(
    "Risk/return monotonicity",
    "Unavailable" if pd.isna(score) else f"{score:.0%}",
)

st.caption(
    "Monotonicity measures how often median forward returns decline as "
    "historical risk bands increase. It is descriptive, not a forecast."
)

st.plotly_chart(build_forward_return_chart(summary, horizon), width="stretch")
st.plotly_chart(build_calibration_chart(calibration), width="stretch")

st.subheader("Forward-return evidence")
display_summary = summary.loc[summary["horizon_days"] == horizon].copy()
st.dataframe(display_summary, width="stretch", hide_index=True)

st.subheader("Cycle stability")
cycle_display = cycles.copy()
cycle_display["start"] = cycle_display["start"].dt.strftime("%d-%b-%Y")
cycle_display["end"] = cycle_display["end"].dt.strftime("%d-%b-%Y")
st.dataframe(cycle_display, width="stretch", hide_index=True)

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        **Method**

        1. OBRM calculates each historical risk value using only data available
           on or before that date.
        2. Future returns are calculated afterward as validation labels.
        3. Outcomes are grouped by the risk band visible on the historical date.
        4. Low-confidence observations can be excluded with the control above.

        **Important limitations**

        - Historical observations overlap, so they are not statistically independent.
        - Bitcoin has passed through only a small number of major market cycles.
        - Results may be sensitive to the chosen horizons and risk thresholds.
        - This is not proof of future performance or financial advice.
        """
    )
