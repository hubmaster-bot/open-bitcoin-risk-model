"""Capital-flow outcome validation and formal promotion-review page."""
import pandas as pd
import streamlit as st

from obrm.research.capital_flow_validation import build_outcome_report, report_frame

st.set_page_config(page_title="Capital Flow Outcome Validation", layout="wide")
st.title("Capital Flow Outcome Validation")
st.caption("v0.10.5 research surface. Promotion eligibility does not modify Composite Risk.")
st.info("Upload a daily CSV containing date, price_usd, and capital_flow_research_score. Future outcomes are evaluation labels only.")

uploaded = st.file_uploader("Outcome-validation CSV", type="csv")
provider_uploads = {}
with st.expander("Optional provider score robustness"):
    for provider in ("coin_metrics", "glassnode", "cryptoquant"):
        item = st.file_uploader(f"{provider} score CSV", type="csv", key=provider)
        if item is not None:
            provider_uploads[provider] = pd.read_csv(item)

if uploaded is not None and st.button("Run outcome validation", type="primary"):
    try:
        report = build_outcome_report(pd.read_csv(uploaded), provider_scores=provider_uploads)
        c1, c2, c3 = st.columns(3)
        c1.metric("Validation", report.overall_status.upper())
        c2.metric("Promotion review", report.promotion_decision.replace("_", " ").upper())
        c3.metric("Live model changed", "NO")
        st.dataframe(report_frame(report), use_container_width=True)
        st.write("Walk-forward stability", report.walk_forward)
        st.write("Provider robustness", report.provider_robustness)
        st.write("Rationale", list(report.rationale))
        st.caption(f"Input hash: {report.generated_from_hash}")
    except Exception as exc:
        st.error(str(exc))
