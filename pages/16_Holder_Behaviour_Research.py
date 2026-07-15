"""Portable Holder Behaviour evidence import and research page."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.evidence.holder_behaviour import VALID_METRIC_KINDS
from obrm.evidence.holder_behaviour_explainability import (
    explain_holder_behaviour_row,
    holder_behaviour_label,
)
from obrm.evidence.holder_behaviour_paths import HOLDER_BEHAVIOUR_METADATA_FILE
from obrm.evidence.holder_behaviour import load_holder_behaviour_metadata
from obrm.evidence.holder_behaviour_service import (
    import_holder_behaviour_csv,
    load_holder_behaviour_analytics,
)


st.set_page_config(
    page_title="OBRM Holder Behaviour Research",
    page_icon="🪙",
    layout="wide",
)


def build_chart(frame: pd.DataFrame) -> go.Figure:
    plotted = frame.dropna(subset=["holder_behaviour_research_score"]).copy()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["holder_metric_value"],
            mode="lines",
            name=str(plotted["provider_metric"].iloc[-1]),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["holder_behaviour_research_score"],
            mode="lines",
            name="Holder Behaviour Research Score",
        ),
        secondary_y=True,
    )
    fig.update_yaxes(title_text="Provider metric", secondary_y=False)
    fig.update_yaxes(
        title_text="Distribution-risk score",
        range=[0, 1],
        secondary_y=True,
    )
    fig.update_layout(
        title="Holder Behaviour Evidence",
        xaxis_title="Date",
        hovermode="x unified",
        height=680,
        legend={"orientation": "h", "y": 1.08, "yanchor": "bottom"},
    )
    return fig


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Holder Behaviour Research")

st.warning(
    "v0.10.2 provides a provider-neutral research pipeline. Imported data must "
    "have a documented definition and licence. The resulting score remains "
    "outside the live model."
)

with st.expander("Import reviewed daily CSV", expanded=False):
    uploaded = st.file_uploader("Daily CSV", type=["csv"])
    if uploaded is not None:
        try:
            preview = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"CSV could not be read: {exc}")
        else:
            st.dataframe(preview.head(20), width="stretch", hide_index=True)
            columns = list(preview.columns)
            left, right = st.columns(2)
            with left:
                date_column = st.selectbox("Date column", columns)
                value_column = st.selectbox("Metric value column", columns)
                metric_kind = st.selectbox(
                    "Metric kind",
                    sorted(VALID_METRIC_KINDS),
                )
                provider = st.text_input("Provider or dataset owner")
            with right:
                provider_metric = st.text_input("Provider metric name")
                definition = st.text_area("Exact metric definition")
                licence_note = st.text_area("Licence / usage note")
                source_url = st.text_input("Source URL (optional)")

            acknowledged = st.checkbox(
                "I have reviewed the source, definition, and permission to use this dataset."
            )
            if st.button("Import Holder Behaviour dataset", disabled=not acknowledged):
                try:
                    analytics, metadata = import_holder_behaviour_csv(
                        preview,
                        date_column=date_column,
                        value_column=value_column,
                        provider=provider,
                        provider_metric=provider_metric,
                        metric_kind=metric_kind,
                        definition=definition,
                        licence_note=licence_note,
                        source_url=source_url or None,
                    )
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.success(
                        f"Imported {len(analytics):,} daily rows from {metadata.provider}."
                    )
                    st.rerun()

try:
    analytics = load_holder_behaviour_analytics()
except (FileNotFoundError, ValueError) as exc:
    st.info(str(exc))
    st.stop()

latest_available = analytics.dropna(subset=["holder_behaviour_research_score"])
if latest_available.empty:
    st.warning("The imported dataset has not accumulated enough history for a score.")
    st.stop()

latest = latest_available.iloc[-1]
metadata = load_holder_behaviour_metadata(HOLDER_BEHAVIOUR_METADATA_FILE)

st.subheader("Current research snapshot")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Provider metric", str(latest["provider_metric"]))
m2.metric("Raw value", f"{latest['holder_metric_value']:,.4g}")
m3.metric("Research score", f"{latest['holder_behaviour_research_score']:.2f}")
m4.metric("Interpretation", holder_behaviour_label(latest["holder_behaviour_research_score"]))

st.plotly_chart(build_chart(analytics), width="stretch")

st.subheader("Interpretation")
for note in explain_holder_behaviour_row(latest):
    st.write(f"- {note}")

st.subheader("Provenance")
if metadata:
    st.json(metadata, expanded=False)

with st.expander("Raw research calculations", expanded=False):
    columns = [
        "date",
        "holder_metric_value",
        "holder_metric_percentile",
        "holder_metric_change_90d",
        "holder_behaviour_score_raw",
        "holder_behaviour_research_score",
        "holder_behaviour_input_coverage",
    ]
    st.dataframe(
        analytics[columns].tail(365).sort_values("date", ascending=False),
        width="stretch",
        hide_index=True,
    )

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        - The importer requires daily dates, numeric non-negative values, and at least 365 rows.
        - Scores use expanding no-look-ahead percentile ranks.
        - Dormancy, coin-days-destroyed, and distribution metrics score higher when old-coin spending rises.
        - Long-term-holder or dormant-supply percentages are inverted so stronger conviction scores lower.
        - A 30-day average reduces noise.
        - Provider definitions are not assumed equivalent across datasets.
        - The signal remains research-only until provider and historical validation are complete.
        """
    )
