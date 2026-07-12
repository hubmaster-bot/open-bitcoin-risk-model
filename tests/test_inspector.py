"""Tests for the v0.4.3 Research Inspector."""

import pandas as pd

from obrm.dashboard.inspector import (
    CROSSHAIR_COLOUR,
    FAIR_VALUE_COLOUR,
    build_chart_figure,
    build_chart_with_inspector_html,
)


def _sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "price_usd": [100.0, 110.0],
            "fair_value_usd": [90.0, 95.0],
            "premium_pct": [11.1, 15.8],
            "price_position_risk": [0.55, 0.60],
            "preliminary_confidence": [0.90, 0.70],
            "market_phase": ["Neutral", "Neutral"],
            "dca_multiplier": [1.0, 1.0],
            "dca_label": ["Normal DCA", "Normal DCA"],
            "provider": ["Test", "Test"],
        }
    )


def test_legend_is_above_plot_area() -> None:
    figure = build_chart_figure(_sample())
    assert figure.layout.margin.t >= 140
    assert figure.layout.legend.yanchor == "bottom"


def test_click_to_inspect_and_crosshair_are_present() -> None:
    output = build_chart_with_inspector_html(_sample())
    assert "plotly_click" in output
    assert 'addEventListener("click"' in output
    assert "lockCrosshair" in output
    assert CROSSHAIR_COLOUR in output


def test_fair_value_remains_solid_green() -> None:
    figure = build_chart_figure(_sample())
    trace = figure.data[1]
    assert trace.line.color == FAIR_VALUE_COLOUR
    assert trace.line.dash is None
