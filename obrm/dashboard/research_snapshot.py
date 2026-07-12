"""Native Plotly historical research snapshot."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PRICE_COLOUR = "#5DADE2"
FAIR_VALUE_COLOUR = "#2ECC71"
RISK_COLOUR = "#FF9AA2"


def build_research_snapshot_chart(df: pd.DataFrame) -> go.Figure:
    """Build the stable native Plotly chart with expanded hover evidence."""
    plotted = df.dropna(
        subset=[
            "fair_value_usd",
            "price_position_risk",
            "momentum_risk",
            "volatility_risk",
            "composite_risk",
            "confidence_v1",
        ]
    ).copy()

    customdata = list(
        zip(
            plotted["date"].dt.strftime("%d-%b-%Y"),
            plotted["fair_value_usd"],
            plotted["premium_pct"],
            plotted["price_position_risk"],
            plotted["momentum_risk"],
            plotted["volatility_risk"],
            plotted["composite_risk"],
            plotted["confidence_v1"],
            plotted["market_phase"],
            plotted["decision_label"],
            plotted["dca_in_multiplier"],
            plotted["dca_out_pct_weekly"],
            plotted["provider"],
        )
    )

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["price_usd"],
            mode="lines",
            name="BTC Price",
            line={"color": PRICE_COLOUR, "width": 1.5},
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br><br>"
                "BTC Price: $%{y:,.2f}<br>"
                "Fair Value: $%{customdata[1]:,.2f}<br>"
                "Premium / Discount: %{customdata[2]:+.1f}%<br><br>"
                "<b>Market Dimensions</b><br>"
                "Valuation: %{customdata[3]:.2f}<br>"
                "Momentum: %{customdata[4]:.2f}<br>"
                "Volatility: %{customdata[5]:.2f}<br><br>"
                "Composite Risk: %{customdata[6]:.2f}<br>"
                "Model Confidence: %{customdata[7]:.0%}<br>"
                "Market Phase: %{customdata[8]}<br>"
                "Decision: %{customdata[9]}<br>"
                "DCA In: %{customdata[10]:.2f}× normal<br>"
                "DCA Out: %{customdata[11]:.2f}% weekly<br>"
                "Source: %{customdata[12]}"
                "<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["fair_value_usd"],
            mode="lines",
            name="Log Regression Fair Value",
            line={"color": FAIR_VALUE_COLOUR, "width": 1.5},
            hoverinfo="skip",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=plotted["date"],
            y=plotted["composite_risk"],
            mode="lines",
            name="Composite OBRM Risk",
            line={"color": RISK_COLOUR, "width": 1.5},
            hoverinfo="skip",
        ),
        secondary_y=True,
    )

    fig.update_yaxes(
        title_text="BTC Price (USD, log scale)",
        type="log",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Composite Risk",
        range=[0, 1],
        secondary_y=True,
    )
    fig.update_layout(
        title={
            "text": "Bitcoin Price, Fair Value, and Composite OBRM Risk",
            "x": 0.0,
            "xanchor": "left",
        },
        xaxis_title="Date",
        hovermode="x unified",
        height=820,
        margin={"l": 70, "r": 55, "t": 125, "b": 60},
        legend={
            "orientation": "h",
            "x": 0.0,
            "xanchor": "left",
            "y": 1.08,
            "yanchor": "bottom",
        },
    )
    return fig
