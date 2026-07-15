"""Research-only multi-provider capital-flow validation page."""
import pandas as pd
import streamlit as st

from obrm.research.provider_validation import (
    PROVIDER_CANDIDATES, build_multi_provider_report, canonicalize_provider_series,
    report_frame,
)

st.set_page_config(page_title="Multi-Provider Validation", layout="wide")
st.title("Multi-Provider Capital-Flow Validation")
st.caption("v0.10.4 research surface. Results do not modify Composite Risk.")
st.info("Upload reviewed daily CSV exports. Provider metrics are compared only when their canonical metric and unit mappings match.")

providers = st.multiselect("Providers", list(PROVIDER_CANDIDATES), default=list(PROVIDER_CANDIDATES)[:3])
frames = {}
for provider in providers:
    mapping = PROVIDER_CANDIDATES[provider]
    with st.expander(provider.replace("_", " ").title(), expanded=True):
        st.write(f"Declared metric: `{mapping.provider_metric}`")
        st.write(f"Canonical metric: `{mapping.canonical_metric}` · transformation: `{mapping.transformation}`")
        uploaded = st.file_uploader(f"CSV for {provider}", type="csv", key=provider)
        if uploaded is not None:
            raw = pd.read_csv(uploaded)
            try:
                frames[provider] = canonicalize_provider_series(raw, mapping)
                st.success(f"Loaded {len(frames[provider]):,} canonical observations")
            except Exception as exc:
                st.error(str(exc))

if len(frames) >= 2 and st.button("Run equivalence validation", type="primary"):
    try:
        report = build_multi_provider_report(frames)
        st.metric("Overall status", report.overall_status.upper())
        st.dataframe(report_frame(report), use_container_width=True)
        st.caption(f"Input hash: {report.generated_from_hash}")
    except Exception as exc:
        st.error(str(exc))
