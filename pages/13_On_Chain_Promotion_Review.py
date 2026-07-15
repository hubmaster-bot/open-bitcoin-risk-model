"""Formal promotion review for the On-Chain Market Dimension."""

import pandas as pd
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.research_data.provider_gaps import ONCHAIN_PROVIDER_GAPS
from obrm.validation.promotion import (
    PROMOTION_STATUS_PROMOTE,
    PROMOTION_STATUS_REJECT,
    PROMOTION_STATUS_RESEARCH,
    load_promotion_decision,
)
from obrm.validation.promotion_paths import (
    ONCHAIN_PROMOTION_DECISION_FILE,
)
from obrm.validation.promotion_service import (
    run_onchain_promotion_review,
)


st.set_page_config(
    page_title="OBRM On-Chain Promotion Review",
    page_icon="⚖️",
    layout="wide",
)

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("On-Chain Promotion Review")

st.info(
    "This page converts the v0.9.4 validation result into a formal, "
    "reproducible decision. It does not modify the live model."
)

if st.button("Run formal promotion review"):
    with st.spinner("Rebuilding validation evidence and reviewing readiness..."):
        decision = run_onchain_promotion_review()
    st.success("Promotion review completed and saved locally.")
    st.rerun()

decision = load_promotion_decision(
    ONCHAIN_PROMOTION_DECISION_FILE
)

if decision is None:
    st.warning(
        "No saved promotion review exists yet. Run the review above."
    )
    st.stop()

status = str(decision["status"])

st.subheader("Decision")
d1, d2, d3 = st.columns(3)
d1.metric("Candidate", str(decision["candidate"]))
d2.metric("Promotion status", status.replace("_", " ").upper())
d3.metric(
    "Live model changed",
    "Yes" if decision["live_model_changed"] else "No",
)

if status == PROMOTION_STATUS_PROMOTE:
    st.success(
        "The candidate passed the provisional gate. Promotion still requires "
        "a separate implementation release."
    )
elif status == PROMOTION_STATUS_RESEARCH:
    st.warning(
        "The candidate remains research-only. The evidence is promising but "
        "not complete enough for live-model promotion."
    )
elif status == PROMOTION_STATUS_REJECT:
    st.error(
        "The candidate is not ready for promotion into Composite Risk."
    )

st.subheader("Promotion gate")
gate_rows = pd.DataFrame(
    [
        ("Coverage", decision["coverage_status"]),
        ("Separation", decision["separation_status"]),
        ("Independence", decision["independence_status"]),
        ("Stability", decision["stability_status"]),
        ("Overall readiness", decision["readiness_status"]),
    ],
    columns=["Criterion", "Status"],
)
st.dataframe(gate_rows, width="stretch", hide_index=True)

st.subheader("Rationale")
for reason in decision["rationale"]:
    st.write(f"- {reason}")

st.subheader("Required next actions")
for action in decision["next_actions"]:
    st.write(f"- {action}")

st.subheader("Provider gaps")
gap_rows = pd.DataFrame(
    [
        {
            "Evidence Category": gap.evidence_category,
            "Current Provider": gap.current_provider,
            "Current Status": gap.current_status,
            "Preferred Fallback": gap.preferred_fallback,
            "Notes": gap.notes,
        }
        for gap in ONCHAIN_PROVIDER_GAPS
    ]
)
st.dataframe(gap_rows, width="stretch", hide_index=True)

st.caption(
    f"Saved decision: {ONCHAIN_PROMOTION_DECISION_FILE}"
)
