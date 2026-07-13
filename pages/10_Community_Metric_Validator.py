"""Empirical Coin Metrics Community availability validator."""

import pandas as pd
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.research_data.availability import (
    STATUS_AVAILABLE,
    STATUS_EMPTY,
    STATUS_ERROR,
    STATUS_FORBIDDEN,
    STATUS_SKIPPED,
    load_availability_registry,
)
from obrm.research_data.metric_validator_service import (
    refresh_metric_availability,
)
from obrm.research_data.paths import ONCHAIN_AVAILABILITY_FILE


st.set_page_config(
    page_title="OBRM Community Metric Validator",
    page_icon="🧪",
    layout="wide",
)

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Community Metric Validator")

st.info(
    "The Coin Metrics catalogue lists metrics that exist, but catalogue "
    "presence does not guarantee Community API download access. This page "
    "tests metrics empirically and stores a verified local registry."
)

with st.expander("Validation controls", expanded=True):
    search_text = st.text_input(
        "Optional search terms",
        value="realized,mvrv,sopr,supply,active,fees,hash",
        help=(
            "Comma-separated terms used to narrow the catalogue. "
            "Leave blank to test the entire catalogue."
        ),
    )
    maximum_metrics = st.number_input(
        "Maximum metrics to test",
        min_value=1,
        max_value=1000,
        value=50,
        step=1,
    )
    probe_start = st.text_input(
        "Probe start date",
        value="2025-01-01",
    )

    if st.button("Build verified Community metric registry"):
        terms = tuple(
            part.strip()
            for part in search_text.split(",")
            if part.strip()
        )

        with st.spinner(
            "Testing metrics sequentially against the Community API..."
        ):
            results = refresh_metric_availability(
                search_terms=terms,
                maximum_metrics=int(maximum_metrics),
                probe_start_time=probe_start,
            )

        st.success(
            f"Tested {len(results):,} metrics and saved the verified registry."
        )
        st.rerun()

registry = load_availability_registry(ONCHAIN_AVAILABILITY_FILE)

if registry is None:
    st.warning(
        "No verified Community metric registry exists yet. "
        "Run the validator above."
    )
    st.stop()

results = pd.DataFrame(registry.get("results", []))

st.subheader("Validation summary")
s1, s2, s3, s4 = st.columns(4)
s1.metric("Tested", f"{len(results):,}")
s2.metric(
    "Available",
    f"{(results['status'] == STATUS_AVAILABLE).sum():,}",
)
s3.metric(
    "Forbidden",
    f"{(results['status'] == STATUS_FORBIDDEN).sum():,}",
)
s4.metric(
    "Other",
    f"{results['status'].isin([STATUS_EMPTY, STATUS_ERROR, STATUS_SKIPPED]).sum():,}",
)

status_filter = st.multiselect(
    "Status filter",
    options=[
        STATUS_AVAILABLE,
        STATUS_FORBIDDEN,
        STATUS_EMPTY,
        STATUS_ERROR,
        STATUS_SKIPPED,
    ],
    default=[
        STATUS_AVAILABLE,
        STATUS_FORBIDDEN,
        STATUS_EMPTY,
        STATUS_ERROR,
    ],
)

display = results.loc[results["status"].isin(status_filter)].copy()
if not display.empty:
    st.dataframe(
        display[
            [
                "metric",
                "status",
                "frequency",
                "observations",
                "first_date",
                "last_date",
                "detail",
            ]
        ].sort_values(["status", "metric"]),
        width="stretch",
        hide_index=True,
    )

available = results.loc[
    results["status"] == STATUS_AVAILABLE,
    "metric",
].tolist()

st.subheader("Verified Community metrics")
if available:
    st.write(", ".join(f"`{metric}`" for metric in available))
else:
    st.warning(
        "No tested metrics were downloadable. Broaden or change the search "
        "terms, or add another provider later."
    )

st.caption(
    "The registry records empirical access under the current Community tier. "
    "Availability may change over time, so it can be rebuilt when needed."
)
