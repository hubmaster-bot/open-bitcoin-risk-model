"""Executive, Analyst, and Research views for OBRM."""

import pandas as pd
import streamlit as st

from obrm.analytics.explainability import build_dimension_snapshots
from obrm.analytics.service import build_risk_dataset
from obrm.confidence.explainability import build_model_confidence_snapshot
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.dashboard.contribution_chart import build_contribution_chart
from obrm.dashboard.dimension_cards import render_dimension_cards
from obrm.dashboard.research_snapshot import build_research_snapshot_chart
from obrm.dashboard.view_modes import VIEW_MODES, view_mode_by_key
from obrm.data.engine import MarketDataEngine
from obrm.decision.audit import build_decision_audit


st.set_page_config(
    page_title="OBRM Research Experience",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_research_experience() -> pd.DataFrame:
    prices = MarketDataEngine().get_btc_price_history()
    return build_risk_dataset(prices)


st.title(APP_NAME)
st.caption(f"Version {APP_VERSION}")
st.header("Research Experience")

mode_key = st.segmented_control(
    "Display mode",
    options=[mode.key for mode in VIEW_MODES],
    default="analyst",
    format_func=lambda key: view_mode_by_key(key).label,
)

mode = view_mode_by_key(mode_key or "analyst")
st.caption(mode.description)

analytics = load_research_experience()
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
confidence = build_model_confidence_snapshot(latest)

st.subheader("Executive view")
e1, e2, e3, e4 = st.columns(4)
e1.metric("BTC Price", f"${latest['price_usd']:,.0f}")
e2.metric("Composite Risk", f"{audit.composite_risk:.2f}")
e3.metric("Model Confidence", f"{audit.model_confidence:.0%}")
e4.metric("Decision", audit.decision_label)

st.plotly_chart(
    build_research_snapshot_chart(available),
    width="stretch",
)

if mode.show_dimensions:
    st.subheader("Market Dimensions")
    render_dimension_cards(audit.dimensions)

if mode.show_contributions:
    st.subheader("Contribution Breakdown")
    st.plotly_chart(
        build_contribution_chart(audit.dimensions),
        width="stretch",
    )
    st.caption(
        f"Primary Driver: {audit.primary_driver}. Contributions sum to "
        f"{sum(item.contribution for item in audit.dimensions):.3f}."
    )

if mode.show_confidence_audit:
    st.subheader("Model Confidence Audit")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Overall", f"{confidence.overall:.0%}")
    c2.metric("Coverage", f"{confidence.coverage:.0%}")
    c3.metric("Agreement", f"{confidence.agreement:.0%}")
    c4.metric("Data Quality", f"{confidence.data_quality:.0%}")
    c5.metric("Model Maturity", f"{confidence.model_maturity:.0%}")

with st.expander("Explain This Decision", expanded=mode.key != "executive"):
    st.write(audit.explanation)

if mode.show_raw_inputs:
    st.subheader("Research calculations")

    rows = []
    for item in audit.dimensions:
        rows.append(
            {
                "Market Dimension": item.display_name,
                "Raw Score": item.score,
                "Standard Label": item.label,
                "Weight": item.weight,
                "Weighted Contribution": item.contribution,
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
        column_config={
            "Raw Score": st.column_config.NumberColumn(format="%.4f"),
            "Weight": st.column_config.NumberColumn(format="%.0%%"),
            "Weighted Contribution": st.column_config.NumberColumn(format="%.4f"),
        },
    )

    raw1, raw2, raw3, raw4 = st.columns(4)
    raw1.metric("Fair Value", f"${latest['fair_value_usd']:,.2f}")
    raw2.metric("Premium / Discount", f"{latest['premium_pct']:+.2f}%")
    raw3.metric("30-day Return", f"{latest['return_30d']:+.2%}")
    raw4.metric("90-day Return", f"{latest['return_90d']:+.2%}")

    raw5, raw6, raw7, raw8 = st.columns(4)
    raw5.metric(
        "30-day Realised Volatility",
        f"{latest['realised_volatility_30d']:.2%}",
    )
    raw6.metric(
        "Drawdown from ATH",
        f"{latest['drawdown_from_ath']:.2%}",
    )
    raw7.metric(
        "200-day MA Distance",
        f"{latest['distance_from_200d_ma']:+.2%}",
    )
    raw8.metric(
        "Regression R²",
        f"{latest['regression_r_squared']:.4f}",
    )

if mode.show_methodology:
    with st.expander("Methodology", expanded=True):
        st.markdown(
            """
            **Composite Risk**

            `Valuation × 45% + Momentum × 30% + Volatility × 25%`

            **Model Confidence**

            Combines Model Maturity, Market Dimension Agreement, Coverage,
            and Data Quality.

            **Historical chart hover**

            Uses native Plotly interaction for stability. The hover snapshot
            displays price, fair value, all current Market Dimensions,
            Composite Risk, Model Confidence, decision, DCA settings, and source.

            **Important**

            OBRM is a research framework, not a prediction engine or personalised
            financial advice.
            """
        )
