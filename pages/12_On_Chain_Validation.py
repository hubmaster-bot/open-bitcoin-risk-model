"""On-Chain Validation Lab."""

import pandas as pd
import plotly.express as px
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.validation.service import load_onchain_validation_report


st.set_page_config(
    page_title="OBRM On-Chain Validation",
    page_icon="🧭",
    layout="wide",
)

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("On-Chain Validation Lab")

st.info(
    "This lab tests whether the provisional on-chain research layer adds "
    "independent, historically useful evidence beyond the existing model."
)

try:
    report = load_onchain_validation_report()
except (FileNotFoundError, ValueError) as exc:
    st.warning(str(exc))
    st.stop()

st.subheader("Validation coverage")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Usable rows", f"{report.usable_rows:,}")
c2.metric("Total rows", f"{report.total_rows:,}")
c3.metric("Usable start", report.usable_start or "Unavailable")
c4.metric("Usable end", report.usable_end or "Unavailable")

st.subheader("Forward-return bucket analysis")
horizon_options = [30, 90, 180, 365, 730]
selected_horizon = st.selectbox(
    "Forward-return horizon",
    options=horizon_options,
    index=3,
    format_func=lambda value: f"{value} days",
)

mean_column = f"{selected_horizon}d_mean"
median_column = f"{selected_horizon}d_median"

bucket_display = report.bucket_summary[
    [
        "score_bucket",
        "observations",
        mean_column,
        median_column,
    ]
].copy()

st.dataframe(
    bucket_display,
    width="stretch",
    hide_index=True,
    column_config={
        mean_column: st.column_config.NumberColumn(format="%.1%%"),
        median_column: st.column_config.NumberColumn(format="%.1%%"),
    },
)

chart_frame = bucket_display.dropna(subset=[mean_column])
if not chart_frame.empty:
    chart = px.bar(
        chart_frame,
        x="score_bucket",
        y=mean_column,
        labels={
            "score_bucket": "On-Chain Score Band",
            mean_column: f"Average {selected_horizon}-day return",
        },
        title=f"Average {selected_horizon}-Day Return by On-Chain Score Band",
    )
    st.plotly_chart(chart, width="stretch")

ratio = report.monotonicity_by_horizon.get(selected_horizon)
st.metric(
    "Band-ordering score",
    "Unavailable" if ratio is None else f"{ratio:.0%}",
    help=(
        "Percentage of adjacent score-band comparisons where higher risk "
        "was followed by lower average future returns."
    ),
)

st.subheader("Subdimension validation")
subdimension = st.radio(
    "Subdimension",
    options=list(report.subdimension_bucket_summary),
    horizontal=True,
)
sub_summary = report.subdimension_bucket_summary[subdimension]
st.dataframe(
    sub_summary,
    width="stretch",
    hide_index=True,
)

st.subheader("Correlation and redundancy")
st.dataframe(
    report.correlations.style.format("{:.2f}"),
    width="stretch",
)

if report.strongest_existing_correlation_name is not None:
    st.write(
        f"Strongest correlation with an existing model signal: "
        f"**{report.strongest_existing_correlation_name}** "
        f"({report.strongest_existing_correlation_value:+.2f})."
    )

st.subheader("Incremental model comparison")
st.dataframe(
    report.incremental_comparison,
    width="stretch",
    hide_index=True,
    column_config={
        "90d_monotonicity": st.column_config.NumberColumn(format="%.0%%"),
        "365d_monotonicity": st.column_config.NumberColumn(format="%.0%%"),
        "730d_monotonicity": st.column_config.NumberColumn(format="%.0%%"),
        "mean_monotonicity": st.column_config.NumberColumn(format="%.0%%"),
    },
)

st.caption(
    "Research Composite v2 is used only inside this validation experiment. "
    "It assigns 20% to the provisional on-chain score and 80% to Composite Risk v1."
)

st.subheader("Market Dimension readiness")
readiness = report.readiness

r1, r2, r3, r4, r5 = st.columns(5)
r1.metric("Coverage", readiness.coverage_status.title())
r2.metric("Separation", readiness.separation_status.title())
r3.metric("Independence", readiness.independence_status.title())
r4.metric("Stability", readiness.stability_status.title())
r5.metric("Overall", readiness.overall_status.upper())

for reason in readiness.reasons:
    st.write(f"- {reason}")

if readiness.overall_status == "ready":
    st.success(
        "The provisional promotion criteria passed. A separate release may "
        "promote On-Chain into Composite Risk after review."
    )
elif readiness.overall_status == "research only":
    st.warning(
        "The evidence is promising but incomplete. Keep the signal in the "
        "research layer while gathering more evidence."
    )
else:
    st.error(
        "The On-Chain Research Score is not ready for promotion into "
        "Composite Risk."
    )

with st.expander("Methodology and safeguards"):
    st.markdown(
        """
        - Historical scores use expanding, no-look-ahead normalization.
        - Forward returns are added only after model scores are calculated.
        - Correlation tests redundancy with current Market Dimensions.
        - Research Composite v2 is experimental and never enters live decisions.
        - Readiness thresholds are provisional and fully visible.
        - Overlapping forward-return windows are not independent observations.
        """
    )
