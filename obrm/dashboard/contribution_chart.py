"""Contribution-breakdown visualization."""

import pandas as pd
import plotly.graph_objects as go

from obrm.analytics.explainability import DimensionSnapshot


def build_contribution_chart(
    dimensions: tuple[DimensionSnapshot, ...],
) -> go.Figure:
    frame = pd.DataFrame(
        {
            "dimension": [item.display_name for item in dimensions],
            "contribution": [item.contribution for item in dimensions],
            "score": [item.score for item in dimensions],
            "weight": [item.weight for item in dimensions],
        }
    ).sort_values("contribution", ascending=True)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=frame["contribution"],
            y=frame["dimension"],
            orientation="h",
            customdata=frame[["score", "weight"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Contribution: %{x:.3f}<br>"
                "Dimension score: %{customdata[0]:.2f}<br>"
                "Weight: %{customdata[1]:.0%}"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Contribution Breakdown",
        xaxis_title="Contribution to Composite Risk",
        yaxis_title="",
        height=360,
        margin={"l": 90, "r": 30, "t": 70, "b": 50},
    )
    return fig
