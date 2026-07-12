"""Reusable Streamlit market-dimension cards."""

import html
import streamlit as st

from obrm.analytics.explainability import DimensionSnapshot


def render_dimension_cards(snapshots: tuple[DimensionSnapshot, ...]) -> None:
    columns = st.columns(len(snapshots))

    for column, snapshot in zip(columns, snapshots, strict=True):
        with column:
            st.markdown(
                f"""
                <div style="
                    border:1px solid rgba(128,128,128,0.35);
                    border-radius:10px;
                    padding:18px;
                    min-height:235px;
                ">
                    <div style="font-size:1.05rem;font-weight:650;">
                        {html.escape(snapshot.display_name)}
                    </div>
                    <div style="font-size:2rem;font-weight:750;margin-top:8px;">
                        {snapshot.score:.2f}
                    </div>
                    <div style="font-size:0.95rem;opacity:0.8;margin-bottom:14px;">
                        {html.escape(snapshot.label)}
                    </div>
                    <div style="font-size:0.88rem;line-height:1.45;">
                        {html.escape(snapshot.explanation)}
                    </div>
                    <div style="font-size:0.78rem;opacity:0.65;margin-top:14px;">
                        Weight {snapshot.weight:.0%} · Contribution {snapshot.contribution:.3f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
