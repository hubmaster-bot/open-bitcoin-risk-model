"""Fallback-provider discovery and assessment page."""

import pandas as pd
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.evidence.discovery_paths import PROVIDER_DISCOVERY_FILE
from obrm.evidence.discovery_service import (
    list_candidates_for_evidence,
    load_saved_assessments,
    record_provider_assessment,
)
from obrm.evidence.service import evidence_by_key


st.set_page_config(
    page_title="OBRM Provider Discovery",
    page_icon="🔭",
    layout="wide",
)

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Fallback Provider Discovery")

st.info(
    "Provider candidates are hypotheses, not approved data sources. A source "
    "must pass access, cost, coverage, definition, reproducibility, and "
    "licensing review before it can satisfy a logical evidence item."
)

missing_keys = ("holder_behaviour", "realized_capital_flow")
selected_evidence = st.selectbox(
    "Missing evidence",
    options=missing_keys,
    format_func=lambda key: evidence_by_key(key).display_name,
)

evidence = evidence_by_key(selected_evidence)
st.write(f"**Research question:** {evidence.purpose}")

candidates = list_candidates_for_evidence(selected_evidence)

st.subheader("Candidate providers")
candidate_rows = pd.DataFrame(
    [
        {
            "Provider": candidate.display_name,
            "Type": candidate.provider_type,
            "Status": candidate.status.replace("_", " ").title(),
            "Access Method": candidate.access_method,
            "Expected Cost": candidate.expected_cost,
            "Priority": candidate.priority,
            "Notes": candidate.notes,
        }
        for candidate in candidates
    ]
)
st.dataframe(candidate_rows, width="stretch", hide_index=True)

st.subheader("Structured provider review")
provider_key = st.selectbox(
    "Provider to assess",
    options=[candidate.key for candidate in candidates],
    format_func=lambda key: next(
        item.display_name for item in candidates if item.key == key
    ),
)

selected_candidate = next(item for item in candidates if item.key == provider_key)
if selected_candidate.source_url:
    st.write(f"Source: `{selected_candidate.source_url}`")
if selected_candidate.documentation_url:
    st.write(f"Documentation: `{selected_candidate.documentation_url}`")

left, right = st.columns(2)
with left:
    access_confirmed = st.checkbox("Access method confirmed")
    free_access_confirmed = st.checkbox("Free access confirmed")
    historical_coverage_confirmed = st.checkbox(
        "Historical coverage confirmed"
    )
with right:
    metric_definition_confirmed = st.checkbox(
        "Metric definition confirmed"
    )
    reproducibility_confirmed = st.checkbox(
        "Reproducibility confirmed"
    )
    licensing_confirmed = st.checkbox("Licensing confirmed")

if st.button("Save provider assessment"):
    assessment = record_provider_assessment(
        provider_key=provider_key,
        evidence_key=selected_evidence,
        access_confirmed=access_confirmed,
        free_access_confirmed=free_access_confirmed,
        historical_coverage_confirmed=historical_coverage_confirmed,
        metric_definition_confirmed=metric_definition_confirmed,
        reproducibility_confirmed=reproducibility_confirmed,
        licensing_confirmed=licensing_confirmed,
    )
    st.success(
        f"Saved assessment: {assessment.status.replace('_', ' ').title()} "
        f"({assessment.score:.0%})."
    )
    st.rerun()

st.subheader("Saved assessments")
saved = load_saved_assessments()
if not saved:
    st.warning("No provider assessments have been saved yet.")
else:
    assessment_frame = pd.DataFrame(saved)
    st.dataframe(
        assessment_frame,
        width="stretch",
        hide_index=True,
        column_config={
            "score": st.column_config.ProgressColumn(
                min_value=0.0,
                max_value=1.0,
                format="%.0%%",
            )
        },
    )

st.caption(
    f"Local discovery registry: {PROVIDER_DISCOVERY_FILE}. "
    "A suitable assessment still requires a separate provider-adapter release."
)
