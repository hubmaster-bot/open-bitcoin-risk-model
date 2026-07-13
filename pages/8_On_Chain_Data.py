"""Coin Metrics Community capability and data-health console."""

import pandas as pd
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.research_data.candidates import CANDIDATE_THEMES
from obrm.research_data.catalog import (
    filter_capabilities,
    load_metric_catalog,
)
from obrm.research_data.engine import OnChainDataEngine
from obrm.research_data.paths import (
    ONCHAIN_CATALOG_FILE,
    ONCHAIN_DATA_FILE,
    ONCHAIN_METADATA_FILE,
)
from obrm.research_data.storage import load_research_metadata


st.set_page_config(
    page_title="OBRM On-Chain Data",
    page_icon="⛓️",
    layout="wide",
)

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("On-Chain Data Engine")

st.info(
    "v0.9.0 discovers and validates Coin Metrics Community capabilities. "
    "It does not add an On-Chain Market Dimension yet."
)

engine = OnChainDataEngine()

if st.button("Refresh Coin Metrics BTC catalogue"):
    with st.spinner("Discovering Coin Metrics Community metrics..."):
        capabilities = engine.refresh_catalog("btc")
    st.success(f"Saved {len(capabilities):,} BTC metric capabilities.")
    st.rerun()

catalog = load_metric_catalog(ONCHAIN_CATALOG_FILE)

if catalog is None:
    st.warning(
        "No local capability catalogue exists yet. Refresh the catalogue "
        "before choosing any metric for v0.9.1."
    )
else:
    st.subheader("Provider capability catalogue")
    st.caption(
        f"Generated: {catalog['generated_at_utc']} · "
        f"Metrics discovered: {catalog['count']:,}"
    )

    raw_metrics = catalog.get("metrics", [])
    frame = pd.DataFrame(raw_metrics)

    search = st.text_input(
        "Search metric names and descriptions",
        placeholder="Try realized, supply, spent, profit, active...",
    )

    if search and not frame.empty:
        mask = (
            frame["metric"].str.contains(search, case=False, na=False)
            | frame["description"].fillna("").str.contains(
                search,
                case=False,
                na=False,
            )
        )
        frame = frame.loc[mask]

    if not frame.empty:
        display = frame.copy()
        display["frequencies"] = display["frequencies"].map(
            lambda values: ", ".join(values)
            if isinstance(values, list)
            else str(values)
        )
        st.dataframe(
            display[
                [
                    "metric",
                    "frequencies",
                    "min_time",
                    "max_time",
                    "description",
                ]
            ],
            width="stretch",
            hide_index=True,
        )
    else:
        st.info("No catalogue metrics match the current search.")

st.subheader("Candidate research themes")
st.dataframe(
    pd.DataFrame(
        CANDIDATE_THEMES,
        columns=["Theme", "Question for v0.9.1"],
    ),
    width="stretch",
    hide_index=True,
)

st.caption(
    "Candidate themes are research questions, not hard-coded provider metric names. "
    "Exact Coin Metrics identifiers will be selected only after catalogue review."
)

st.subheader("Canonical on-chain dataset status")
metadata = load_research_metadata(ONCHAIN_METADATA_FILE)

if metadata is None:
    st.warning(
        "No canonical on-chain dataset has been selected or downloaded. "
        "This is expected in v0.9.0."
    )
else:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Rows", f"{metadata['rows']:,}")
    m2.metric("Coverage start", metadata["coverage_start"])
    m3.metric("Coverage end", metadata["coverage_end"])
    m4.metric(
        "Freshness",
        (
            f"Stale · {metadata['days_behind_utc']} days"
            if metadata["is_stale"]
            else "Healthy"
        ),
    )
    st.write(f"**Metrics:** {', '.join(metadata['metrics'])}")
    st.write(f"**SHA-256:** `{metadata['sha256']}`")
    st.write(f"**Local file:** `{ONCHAIN_DATA_FILE}`")

with st.expander("Provider architecture"):
    st.markdown(
        """
        External provider → Provider adapter → Schema normalization →
        Validation and provenance → Canonical local dataset → Analytics.

        The future On-Chain Analytics layer will depend on the canonical schema,
        not directly on Coin Metrics field names or network behaviour.
        """
    )
