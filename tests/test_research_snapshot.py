"""Tests for the stable native Plotly research snapshot."""

import pandas as pd

from obrm.dashboard.research_snapshot import (
    FAIR_VALUE_COLOUR,
    build_research_snapshot_chart,
)


def _sample() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "price_usd": [100.0, 110.0],
            "fair_value_usd": [90.0, 95.0],
            "premium_pct": [11.1, 15.8],
            "price_position_risk": [0.55, 0.60],
            "momentum_risk": [0.40, 0.50],
            "volatility_risk": [0.30, 0.35],
            "composite_risk": [0.45, 0.50],
            "confidence_v1": [0.90, 0.91],
            "market_phase": ["Neutral", "Neutral"],
            "decision_label": ["Normal DCA", "Normal DCA"],
            "dca_in_multiplier": [1.0, 1.0],
            "dca_out_pct_weekly": [0.0, 0.0],
            "provider": ["Test", "Test"],
        }
    )


def test_snapshot_uses_native_unified_hover() -> None:
    figure = build_research_snapshot_chart(_sample())
    assert figure.layout.hovermode == "x unified"


def test_snapshot_contains_three_traces() -> None:
    figure = build_research_snapshot_chart(_sample())
    assert len(figure.data) == 3


def test_fair_value_remains_green() -> None:
    figure = build_research_snapshot_chart(_sample())
    assert figure.data[1].line.color == FAIR_VALUE_COLOUR


def test_legend_sits_above_plot() -> None:
    figure = build_research_snapshot_chart(_sample())
    assert figure.layout.legend.y > 1.0
