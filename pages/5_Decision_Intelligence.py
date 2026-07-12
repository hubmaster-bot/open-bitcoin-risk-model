"""Decision Audit and explainability page."""

import pandas as pd
import streamlit as st

from obrm.analytics.service import build_risk_dataset
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.dashboard.contribution_chart import build_contribution_chart
from obrm.data.engine import MarketDataEngine
from obrm.decision.audit import build_decision_audit
from obrm.decision.thresholds import DECISION_THRESHOLDS


st.set_page_config(
    page_title="OBRM Decision Intelligence",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data
def load_decision_intelligence() -> pd.DataFrame:
    prices = MarketDataEngine().get_btc_price_history()
    return build_risk_dataset(prices)


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Decision Intelligence")

analytics = load_decision_intelligence()
available = analytics.dropna(
    subset=[
        "composite_risk",
        "confidence_v1",
        "price_position_risk",
        "momentum_risk",
        "volatility_risk",
    ]
)
latest = available.iloc[-1]
audit = build_decision_audit(latest)

st.subheader("Decision Audit")
a1, a2, a3, a4 = st.columns(4)
a1.metric("Composite Risk", f"{audit.composite_risk:.2f}")
a2.metric("Model Confidence", f"{audit.model_confidence:.0%}")
a3.metric("Decision", audit.decision_label)
a4.metric("Primary Driver", audit.primary_driver)

st.subheader("Market Dimensions")
dimension_rows = pd.DataFrame(
    [
        {
            "Market Dimension": item.display_name,
            "Score": item.score,
            "Label": item.label,
            "Weight": item.weight,
            "Contribution": item.contribution,
        }
        for item in audit.dimensions
    ]
)
st.dataframe(
    dimension_rows,
    width="stretch",
    hide_index=True,
    column_config={
        "Score": st.column_config.NumberColumn(format="%.2f"),
        "Weight": st.column_config.NumberColumn(format="%.0%%"),
        "Contribution": st.column_config.NumberColumn(format="%.3f"),
    },
)

st.plotly_chart(build_contribution_chart(audit.dimensions), width="stretch")

st.subheader("Model Confidence Audit")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Overall", f"{audit.confidence.overall:.0%}")
c2.metric("Coverage", f"{audit.confidence.coverage:.0%}")
c3.metric("Agreement", f"{audit.confidence.agreement:.0%}")
c4.metric("Data Quality", f"{audit.confidence.data_quality:.0%}")
c5.metric("Model Maturity", f"{audit.confidence.model_maturity:.0%}")

with st.expander("Explain This Decision", expanded=True):
    st.write(audit.explanation)

st.subheader("Decision Thresholds")
threshold_rows = pd.DataFrame(
    [
        {
            "Risk Range": f"{item.minimum_risk:.2f}–{item.maximum_risk:.2f}",
            "Decision": item.label,
            "Action": item.action,
            "DCA In": f"{item.dca_in_multiplier:.2f}×",
            "DCA Out": f"{item.dca_out_pct_weekly:.2f}%/week",
        }
        for item in DECISION_THRESHOLDS
    ]
)
st.dataframe(threshold_rows, width="stretch", hide_index=True)

st.caption(
    "Decision thresholds remain research-alpha settings and require continued "
    "validation before they should influence real transactions."
)
