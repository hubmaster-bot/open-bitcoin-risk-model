"""On-chain analytics research page."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.onchain.explainability import explain_onchain_row
from obrm.onchain.service import (
    load_selected_onchain_analytics,
    refresh_selected_onchain_data,
)


st.set_page_config(
    page_title="OBRM On-Chain Analytics",
    page_icon="🧬",
    layout="wide",
)


def build_onchain_chart(frame: pd.DataFrame) -> go.Figure:
    plotted = frame.dropna(
        subset=["mvrv", "onchain_research_score"]
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
            y=plotted["onchain_research_score"],
            mode="lines",
            name="On-Chain Research Score",
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="MVRV", secondary_y=False)
    fig.update_yaxes(
        title_text="Research Score",
        range=[0, 1],
        secondary_y=True,
    )
    fig.update_layout(
        title="On-Chain Research Signals",
        xaxis_title="Date",
        hovermode="x unified",
        height=650,
        legend={
            "orientation": "h",
            "y": 1.08,
            "yanchor": "bottom",
        },
    )
    return fig


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("On-Chain Analytics")

st.warning(
    "v0.9.1 introduces diagnostic on-chain analytics only. "
    "These values do not yet alter Composite Risk, Model Confidence, "
    "Decision Engine outputs, backtests, or portfolio guidance."
)

if st.button("Refresh selected Coin Metrics analytics"):
    with st.spinner("Resolving catalogue metrics and downloading data..."):
        refreshed, resolution = refresh_selected_onchain_data()
    st.success(
        f"Downloaded {len(refreshed):,} daily observations using "
        f"{len(resolution.resolved)} resolved metrics."
    )
    st.rerun()

try:
    analytics, resolution = load_selected_onchain_analytics()
except (FileNotFoundError, ValueError) as exc:
    st.info(str(exc))
    st.stop()

latest_available = analytics.dropna(
    subset=["mvrv", "onchain_research_score"]
)
if latest_available.empty:
    st.warning("The cached dataset does not contain usable analytics yet.")
    st.stop()

latest = latest_available.iloc[-1]

st.subheader("Current on-chain research snapshot")
m1, m2, m3, m4 = st.columns(4)
m1.metric("MVRV", f"{latest['mvrv']:.2f}")
m2.metric("Realized Cap", f"${latest['realized_cap_usd']:,.0f}")
m3.metric(
    "365-day Realized Cap Growth",
    f"{latest['realized_cap_growth_365d']:+.1%}",
)
m4.metric("Research Score", f"{latest['onchain_research_score']:.2f}")

st.plotly_chart(build_onchain_chart(analytics), width="stretch")

st.subheader("Resolved Coin Metrics inputs")
resolved_rows = pd.DataFrame(
    [
        {
            "Logical Input": item.display_name,
            "Coin Metrics Identifier": item.provider_metric,
            "Required": item.required,
            "Purpose": item.purpose,
        }
        for item in resolution.resolved
    ]
)
st.dataframe(resolved_rows, width="stretch", hide_index=True)

if resolution.unresolved_optional:
    st.info(
        "Optional inputs unavailable in the current catalogue: "
        + ", ".join(resolution.unresolved_optional)
    )

st.subheader("Interpretation")
for note in explain_onchain_row(latest):
    st.write(f"- {note}")

st.subheader("Research columns")
columns = [
    "date",
    "mvrv",
    "mvrv_percentile",
    "realized_cap_usd",
    "realized_cap_growth_365d",
    "realized_cap_growth_percentile",
    "active_supply_1y",
    "active_supply_1y_percentile",
    "onchain_research_score",
    "onchain_component_coverage",
]
st.dataframe(
    analytics[[column for column in columns if column in analytics.columns]]
    .tail(365)
    .sort_values("date", ascending=False),
    width="stretch",
    hide_index=True,
)

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        **Current diagnostic inputs**

        - MVRV compares market value with realized value.
        - Realized-cap growth approximates changes in aggregate realized value.
        - One-year active supply is optional and depends on Community catalogue availability.

        **Normalization**

        OBRM uses expanding percentile ranks calculated only from information
        available on or before each date. A 30-day average smooths the diagnostic score.

        **Important**

        The score is not yet a Market Dimension. Metric selection, weighting,
        validation, and redundancy analysis continue in v0.9.2 and v0.9.3.
        """
    )
