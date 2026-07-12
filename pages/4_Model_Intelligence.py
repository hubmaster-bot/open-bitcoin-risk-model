"""Market Dimensions and Model Confidence page."""

import pandas as pd
import streamlit as st

from obrm.analytics.explainability import build_dimension_snapshots
from obrm.analytics.service import build_risk_dataset
from obrm.confidence.explainability import (
    build_model_confidence_snapshot,
    confidence_explanation,
)
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.dashboard.dimension_cards import render_dimension_cards
from obrm.data.engine import MarketDataEngine


st.set_page_config(
    page_title="OBRM Model Intelligence",
    page_icon="🧠",
    layout="wide",
)


@st.cache_data
def load_model_intelligence() -> pd.DataFrame:
    prices = MarketDataEngine().get_btc_price_history()
    return build_risk_dataset(prices)


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Model Intelligence")

analytics = load_model_intelligence()
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

st.subheader("Executive view")
e1, e2, e3, e4 = st.columns(4)
e1.metric("BTC Price", f"${latest['price_usd']:,.0f}")
e2.metric("Composite Risk", f"{latest['composite_risk']:.2f}")
e3.metric("Model Confidence", f"{latest['confidence_v1']:.0%}")
e4.metric("Decision", latest["decision_label"])

st.subheader("Market Dimensions")
render_dimension_cards(build_dimension_snapshots(latest))

st.subheader("Model Confidence")
confidence = build_model_confidence_snapshot(latest)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Model Confidence", f"{confidence.overall:.0%}")
c2.metric("Coverage", f"{confidence.coverage:.0%}")
c3.metric("Agreement", f"{confidence.agreement:.0%}")
c4.metric("Data Quality", f"{confidence.data_quality:.0%}")
c5.metric("Model Maturity", f"{confidence.model_maturity:.0%}")

st.info(confidence_explanation(confidence))

with st.expander("Terminology"):
    st.markdown(
        """
        **Market Dimensions** describe different aspects of market conditions.

        - **Valuation** asks where price sits relative to long-term fair value.
        - **Momentum** asks how strongly price is moving.
        - **Volatility** asks how stable or turbulent conditions are.

        **Model Confidence** describes how much trust to place in the model's
        current assessment. It is not the probability that Bitcoin will rise or fall.
        """
    )
