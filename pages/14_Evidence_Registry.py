"""Provider-independent evidence registry and coverage dashboard."""

import pandas as pd
import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION
from obrm.evidence.service import (
    domain_coverage,
    list_evidence,
    mappings_for_evidence,
    onchain_required_coverage,
    overall_coverage,
)


st.set_page_config(
    page_title="OBRM Evidence Registry",
    page_icon="🗂️",
    layout="wide",
)

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Evidence Registry")

st.info(
    "The Evidence Registry describes what OBRM wants to know before deciding "
    "which provider or metric should supply it. Providers are implementation "
    "details; logical evidence remains the stable research concept."
)

all_evidence = list_evidence()
overall = overall_coverage()
onchain = onchain_required_coverage()

st.subheader("Research coverage")
c1, c2, c3 = st.columns(3)
c1.metric(
    "Overall validated evidence",
    f"{overall.validated} of {overall.total}",
)
c2.metric("Overall coverage", f"{overall.ratio:.0%}")
c3.metric(
    "Required On-Chain coverage",
    f"{onchain.validated} of {onchain.total}",
)

st.progress(overall.ratio, text=f"Overall evidence coverage: {overall.ratio:.0%}")
st.progress(onchain.ratio, text=f"Required On-Chain coverage: {onchain.ratio:.0%}")

st.subheader("Coverage by research domain")
domain_rows = pd.DataFrame(
    [
        {
            "Domain": coverage.scope,
            "Validated": coverage.validated,
            "Total": coverage.total,
            "Coverage": coverage.ratio,
        }
        for coverage in domain_coverage()
    ]
)
st.dataframe(
    domain_rows,
    width="stretch",
    hide_index=True,
    column_config={
        "Coverage": st.column_config.ProgressColumn(
            min_value=0.0,
            max_value=1.0,
            format="%.0%%",
        )
    },
)

st.subheader("Canonical evidence")
status_options = sorted({item.status for item in all_evidence})
selected_statuses = st.multiselect(
    "Status filter",
    options=status_options,
    default=status_options,
)

filtered = tuple(
    item for item in all_evidence if item.status in selected_statuses
)

for item in filtered:
    mappings = mappings_for_evidence(item.key)
    status_label = item.status.replace("_", " ").title()

    with st.expander(
        f"{item.display_name} · {status_label}",
        expanded=item.status in {"validated", "missing"},
    ):
        i1, i2, i3, i4 = st.columns(4)
        i1.metric("Domain", item.domain)
        i2.metric("Intended dimension", item.intended_dimension)
        i3.metric("Status", status_label)
        i4.metric(
            "Required",
            "Yes" if item.required_for_dimension else "No",
        )

        st.write(item.purpose)
        st.caption(
            f"Documentation: {item.documentation}"
            + (
                f" · Target: {item.target_version}"
                if item.target_version
                else ""
            )
        )

        if mappings:
            mapping_rows = pd.DataFrame(
                [
                    {
                        "Provider": mapping.provider,
                        "Provider Metric": mapping.provider_metric or "Not selected",
                        "Status": mapping.status.replace("_", " ").title(),
                        "Priority": mapping.priority,
                        "Definition": mapping.definition,
                        "Provenance": mapping.provenance_note,
                    }
                    for mapping in mappings
                ]
            )
            st.dataframe(mapping_rows, width="stretch", hide_index=True)
        else:
            st.warning(
                "No provider mapping has been registered for this evidence yet."
            )

with st.expander("Evidence-first workflow", expanded=True):
    st.markdown(
        """
        1. Define the logical evidence and the question it answers.
        2. Register one or more potential provider mappings.
        3. Validate actual data access, coverage, quality, and definitions.
        4. Build a research signal using no-look-ahead calculations.
        5. Test incremental value and redundancy.
        6. Promote the result only after a formal review.

        A provider failure does not invalidate the evidence concept. OBRM can
        replace the provider, combine multiple providers, accept a user dataset,
        or eventually calculate the evidence from Bitcoin Core.
        """
    )
