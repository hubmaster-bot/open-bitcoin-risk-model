"""In-app documentation hub for OBRM."""

from pathlib import Path

import streamlit as st

from obrm.core.version import APP_NAME, APP_VERSION


st.set_page_config(
    page_title="OBRM Documentation Hub",
    page_icon="📚",
    layout="wide",
)

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Documentation Hub")

st.info(
    "The documentation is organised into a User Guide, Research Handbook, "
    "Developer Guide, Architecture Decision Records, and release notes."
)

sections = {
    "User Guide": [
        ("Getting Started", DOCS / "user_guide" / "01_Getting_Started.md"),
        ("Understanding the Dashboard", DOCS / "user_guide" / "02_Dashboard.md"),
        ("Understanding Recommendations", DOCS / "user_guide" / "03_Recommendations.md"),
        ("Portfolio Lab", DOCS / "user_guide" / "04_Portfolio_Lab.md"),
        ("Validation and Backtesting", DOCS / "user_guide" / "05_Validation.md"),
        ("Limitations and Safety", DOCS / "user_guide" / "06_Limitations.md"),
    ],
    "Research Handbook": [
        ("Introduction", DOCS / "handbook" / "01_Introduction.md"),
        ("Market Dimensions", DOCS / "handbook" / "02_Market_Dimensions.md"),
        ("Model Confidence", DOCS / "handbook" / "03_Model_Confidence.md"),
        ("Composite Risk", DOCS / "handbook" / "04_Composite_Risk.md"),
        ("Decision Audit", DOCS / "handbook" / "05_Decision_Audit.md"),
        ("Research Experience", DOCS / "handbook" / "06_Research_Experience.md"),
        ("Validation Philosophy", DOCS / "handbook" / "07_Validation_Philosophy.md"),
        ("On-Chain Data Foundation", DOCS / "handbook" / "08_OnChain_Data_Foundation.md"),
        ("On-Chain Analytics", DOCS / "handbook" / "09_OnChain_Analytics.md"),
        ("Community Metric Validation", DOCS / "handbook" / "10_Community_Metric_Validation.md"),
        ("Validated On-Chain Research", DOCS / "handbook" / "11_Validated_OnChain_Research.md"),
        ("On-Chain Validation", DOCS / "handbook" / "12_OnChain_Validation.md"),
        ("On-Chain Promotion Review", DOCS / "handbook" / "13_OnChain_Promotion_Review.md"),
        ("Evidence Registry", DOCS / "handbook" / "14_Evidence_Registry.md"),
        ("Fallback Provider Discovery", DOCS / "handbook" / "15_Fallback_Provider_Discovery.md"),
    ],
    "Developer Guide": [
        ("Architecture Overview", DOCS / "developer" / "01_Architecture.md"),
        ("Data Flow", DOCS / "developer" / "02_Data_Flow.md"),
        ("Adding a Market Dimension", DOCS / "developer" / "03_Adding_Dimensions.md"),
        ("Testing and Release Process", DOCS / "developer" / "04_Testing_and_Releases.md"),
        ("Research Data Providers", DOCS / "developer" / "05_Research_Data_Providers.md"),
        ("Evidence Registry", DOCS / "developer" / "06_Evidence_Registry.md"),
        ("Provider Discovery", DOCS / "developer" / "07_Provider_Discovery.md"),
    ],
}

tabs = st.tabs(list(sections))

for tab, (section_name, documents) in zip(tabs, sections.items(), strict=True):
    with tab:
        st.subheader(section_name)
        selected = st.selectbox(
            "Document",
            options=[title for title, _ in documents],
            key=f"doc_{section_name}",
        )
        selected_path = dict(documents)[selected]

        if selected_path.exists():
            st.markdown(selected_path.read_text(encoding="utf-8"))
        else:
            st.warning(f"Documentation file not found: {selected_path}")

st.subheader("Model Maturity Scorecard")

scorecard = [
    ("Price data", "Available", "Validated and provenance tracked"),
    ("Fair value", "Available", "Expanding no-look-ahead log regression"),
    ("Market Dimensions", "Available", "Valuation, Momentum, Volatility"),
    ("Composite Risk", "Available", "Transparent weighted blend"),
    ("Model Confidence", "Available", "Coverage, Agreement, Data Quality, Maturity"),
    ("Decision Engine", "Research Alpha", "DCA-in, pause, and DCA-out"),
    ("Portfolio Layer", "Research Alpha", "Constraint-aware planning"),
    ("Backtesting", "Research Alpha", "Contribution-matched strategy comparison"),
    ("Walk-forward validation", "Research Alpha", "Future returns used as labels only"),
    ("Explainability", "Available", "Decision Audit and progressive disclosure"),
    ("Transaction costs", "Planned", "Fees, spread, slippage, and taxes"),
    ("On-chain research", "Research Alpha", "Validated evidence remains outside Composite Risk"),
    ("Evidence Registry", "Available", "Provider-independent evidence roadmap and coverage"),
    ("Provider Discovery", "Research Alpha", "Structured fallback-source assessment"),
    ("Macro dimensions", "Planned", "Post-v1.0 research"),
]

st.dataframe(
    {
        "Capability": [item[0] for item in scorecard],
        "Status": [item[1] for item in scorecard],
        "Notes": [item[2] for item in scorecard],
    },
    width="stretch",
    hide_index=True,
)

st.caption(
    "Documentation reflects the current research state of OBRM. "
    "Research Alpha features remain provisional and subject to revision."
)
