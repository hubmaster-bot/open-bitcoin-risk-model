"""Portable Realized Capital Flow evidence import and research page."""
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.research.capital_flow import VALID_METRIC_KINDS
from obrm.research.capital_flow.paths import CAPITAL_FLOW_METADATA_FILE
from obrm.research.capital_flow.service import import_capital_flow_csv, load_capital_flow_analytics

st.set_page_config(page_title=f"Realized Capital Flow | {APP_NAME}", layout="wide")
st.title("Realized Capital Flow Research")
st.caption(f"Version {APP_VERSION}")
st.warning("Research-only evidence. This score does not influence Composite Risk or live decisions.")

with st.expander("Import reviewed daily capital-flow CSV", expanded=False):
    uploaded = st.file_uploader("CSV file", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        cols = list(raw.columns)
        c1, c2 = st.columns(2)
        date_column = c1.selectbox("Date column", cols)
        value_column = c2.selectbox("Value column", cols, index=min(1, len(cols)-1))
        provider = st.text_input("Provider")
        provider_metric = st.text_input("Provider metric")
        metric_kind = st.selectbox("Metric kind", sorted(VALID_METRIC_KINDS))
        custom_direction = None
        if metric_kind == "custom_capital_flow":
            custom_direction = st.selectbox("Positive values mean", ["inflow", "outflow"])
        definition = st.text_area("Metric definition")
        licence_note = st.text_input("Licence / usage note")
        source_url = st.text_input("Source URL (optional)")
        if st.button("Validate and import", type="primary"):
            try:
                analytics, metadata = import_capital_flow_csv(
                    raw, date_column=date_column, value_column=value_column,
                    provider=provider, provider_metric=provider_metric,
                    metric_kind=metric_kind, definition=definition,
                    licence_note=licence_note, source_url=source_url or None,
                    custom_positive_direction=custom_direction,
                )
            except (ValueError, OSError) as exc:
                st.error(str(exc))
            else:
                st.success(f"Imported {len(analytics):,} daily rows from {metadata.provider}.")
                st.rerun()

try:
    df = load_capital_flow_analytics()
except (FileNotFoundError, ValueError) as exc:
    st.info(str(exc)); st.stop()
latest_rows = df.dropna(subset=["capital_flow_research_score"])
if latest_rows.empty:
    st.warning("The dataset has not accumulated enough history for a score."); st.stop()
latest = latest_rows.iloc[-1]

m1,m2,m3,m4 = st.columns(4)
m1.metric("Provider metric", str(latest["provider_metric"]))
m2.metric("Raw value", f'{latest["capital_flow_value"]:,.4g}')
m3.metric("Research score", f'{latest["capital_flow_research_score"]:.2f}')
m4.metric("Trend", str(latest["capital_flow_trend_direction"]).title())

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Scatter(x=df.date, y=df.capital_flow_value, name="Raw flow"), secondary_y=False)
fig.add_trace(go.Scatter(x=df.date, y=df.capital_flow_smoothed_30d, name="30-day smooth"), secondary_y=False)
fig.add_trace(go.Scatter(x=df.date, y=df.capital_flow_research_score, name="Research score"), secondary_y=True)
fig.update_yaxes(title_text="Provider units", secondary_y=False)
fig.update_yaxes(title_text="Score (0–1)", range=[0,1], secondary_y=True)
st.plotly_chart(fig, width="stretch")

st.subheader("Provenance and integrity")
if CAPITAL_FLOW_METADATA_FILE.exists():
    st.json(json.loads(CAPITAL_FLOW_METADATA_FILE.read_text(encoding="utf-8")), expanded=False)
with st.expander("Raw research calculations"):
    columns=["date","capital_flow_value","capital_flow_percentile_expanding",
             "capital_flow_smoothed_30d","capital_flow_change_90d",
             "capital_flow_percentile_1y","capital_flow_trend_direction",
             "capital_flow_acceleration","capital_flow_research_score"]
    st.dataframe(df[columns].tail(365).sort_values("date",ascending=False), hide_index=True, width="stretch")
with st.expander("Methodology and limitations"):
    st.markdown("""
- Daily reviewed data and at least 365 usable observations are required.
- Expanding percentiles are no-look-ahead; the yearly percentile uses only the trailing window.
- A 30-day mean reduces noise; 90-day change, trend, and acceleration remain diagnostic.
- Positive-direction semantics are explicit and provider definitions are never assumed equivalent.
- Higher research scores mean stronger net capital inflow, not automatically lower investment risk.
- Multi-provider equivalence is available in v0.10.4 and outcome validation in v0.10.5.
""")
