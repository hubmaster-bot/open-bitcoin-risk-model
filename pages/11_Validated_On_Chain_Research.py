"""Validated on-chain research page."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.onchain.validated_explainability import (
    explain_validated_onchain_row,
)
from obrm.onchain.validated_registry import (
    ONCHAIN_EVIDENCE_CATEGORIES,
    available_evidence_count,
    intended_evidence_count,
)
from obrm.onchain.validated_service import (
    load_validated_onchain_data,
    refresh_validated_onchain_data,
)


st.set_page_config(
    page_title="OBRM Validated On-Chain Research",
    page_icon="🔬",
    layout="wide",
)


def build_validated_chart(frame: pd.DataFrame) -> go.Figure:
    plotted = frame.dropna(
        subset=[
            "mvrv",
            "hash_rate",
            "onchain_research_score",
        ]
    ).copy()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["mvrv"],
            mode="lines",
            name="MVRV",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["network_strength_score"],
            mode="lines",
            name="Network Strength Score",
        ),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["onchain_research_score"],
            mode="lines",
            name="On-Chain Research Score",
        ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text="MVRV", secondary_y=False)
    fig.update_yaxes(
        title_text="Normalized research score",
        range=[0, 1],
        secondary_y=True,
    )
    fig.update_layout(
        title="Validated On-Chain Research Signals",
        xaxis_title="Date",
        hovermode="x unified",
        height=700,
        legend={
            "orientation": "h",
            "y": 1.08,
            "yanchor": "bottom",
        },
    )
    return fig


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Validated On-Chain Research")

st.warning(
    "v0.9.3 uses only Coin Metrics Community inputs that were empirically "
    "validated as downloadable: CapMVRVCur and HashRate. This remains a "
    "diagnostic research layer and does not yet alter Composite Risk."
)

if st.button("Refresh validated on-chain dataset"):
    with st.spinner("Downloading validated Coin Metrics inputs..."):
        refreshed = refresh_validated_onchain_data()
    st.success(
        f"Downloaded and processed {len(refreshed):,} daily observations."
    )
    st.rerun()

try:
    analytics = load_validated_onchain_data()
except (FileNotFoundError, ValueError) as exc:
    st.info(str(exc))
    st.stop()

latest_available = analytics.dropna(
    subset=["mvrv", "hash_rate", "onchain_research_score"]
)
if latest_available.empty:
    st.warning("No usable validated on-chain observations are available.")
    st.stop()

latest = latest_available.iloc[-1]

st.subheader("Current validated snapshot")
m1, m2, m3, m4 = st.columns(4)
m1.metric("MVRV", f"{latest['mvrv']:.2f}")
m2.metric("Hash Rate", f"{latest['hash_rate']:,.2f}")
m3.metric(
    "365-day Hash Rate Growth",
    f"{latest['hash_rate_growth_365d']:+.1%}",
)
m4.metric(
    "On-Chain Research Score",
    f"{latest['onchain_research_score']:.2f}",
)

st.plotly_chart(build_validated_chart(analytics), width="stretch")

st.subheader("Evidence coverage")
coverage1, coverage2 = st.columns(2)
coverage1.metric(
    "Available evidence categories",
    f"{available_evidence_count()} of {intended_evidence_count()}",
)
coverage2.metric(
    "Current row input coverage",
    f"{latest['onchain_input_coverage']:.0%}",
)

evidence_rows = pd.DataFrame(
    [
        {
            "Evidence Category": item.display_name,
            "Provider Metric": item.provider_metric or "Not yet available",
            "Available": item.available,
            "Purpose": item.purpose,
            "Status": item.status_note,
        }
        for item in ONCHAIN_EVIDENCE_CATEGORIES
    ]
)
st.dataframe(evidence_rows, width="stretch", hide_index=True)

st.subheader("Interpretation")
for note in explain_validated_onchain_row(latest):
    st.write(f"- {note}")

st.subheader("Research calculations")
columns = [
    "date",
    "mvrv",
    "mvrv_percentile",
    "hash_rate",
    "hash_rate_growth_365d",
    "hash_rate_vs_trend",
    "network_strength_score",
    "realized_valuation_score",
    "onchain_research_score",
    "onchain_input_coverage",
]
st.dataframe(
    analytics[columns]
    .tail(365)
    .sort_values("date", ascending=False),
    width="stretch",
    hide_index=True,
)

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        **Realized Valuation**

        Uses MVRV and an expanding no-look-ahead percentile rank.

        **Network Strength**

        Combines 365-day hash-rate growth with distance from the 200-day
        hash-rate trend. Both are converted to expanding percentiles.

        **Diagnostic score**

        The current On-Chain Research Score is the equal-weight mean of
        Realized Valuation and Network Strength, smoothed over 30 days.

        **Coverage limitation**

        Only two of four intended evidence categories are available. Holder
        Behaviour and Realized Capital Flow remain missing, so this score is
        not yet promoted into Composite Risk.
        """
    )
