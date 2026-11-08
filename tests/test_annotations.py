from pathlib import Path

import pytest

from obrm.dashboard.annotations import (
    ChartAnnotation,
    annotations_csv,
    annotations_json,
    load_annotations,
    save_annotations,
)


def test_annotation_round_trip(tmp_path: Path):
    path = tmp_path / "annotations.json"
    expected = [
        ChartAnnotation.create("vertical_date", "2026-07-19", "Review"),
        ChartAnnotation.create("horizontal_price", 100_000, "Target"),
        ChartAnnotation.create("horizontal_risk", 0.8, "Caution"),
    ]
    save_annotations(expected, path)
    assert load_annotations(path) == expected


def test_annotation_validation():
    with pytest.raises(ValueError):
        ChartAnnotation.create("horizontal_risk", 1.1)
    with pytest.raises(ValueError):
        ChartAnnotation.create("horizontal_price", 0)
    with pytest.raises(ValueError):
        ChartAnnotation.create("vertical_date", "not-a-date")


def test_exports_include_labels():
    items = [ChartAnnotation.create("horizontal_risk", 0.75, "My level")]
    assert '"My level"' in annotations_json(items)
    assert '"My level"' in annotations_csv(items)


def test_market_chart_renders_all_annotation_types():
    import pandas as pd
    from obrm.dashboard.app import build_market_chart

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "price_usd": [90_000.0, 91_000.0],
            "fair_value_usd": [80_000.0, 80_500.0],
            "premium_pct": [12.5, 13.0],
            "price_position_risk": [0.5, 0.55],
            "momentum_risk": [0.4, 0.45],
            "volatility_risk": [0.3, 0.35],
            "composite_risk": [0.42, 0.47],
            "confidence_v1": [0.9, 0.9],
            "market_phase": ["Neutral", "Neutral"],
            "decision_label": ["Hold", "Hold"],
            "dca_in_multiplier": [1.0, 1.0],
            "dca_out_pct_weekly": [0.0, 0.0],
            "provider": ["Test", "Test"],
        }
    )
    annotations = [
        ChartAnnotation.create("vertical_date", "2026-01-01", "Date"),
        ChartAnnotation.create("horizontal_price", 100_000, "Price"),
        ChartAnnotation.create("horizontal_risk", 0.8, "Risk"),
    ]
    figure = build_market_chart(frame, annotations)
    assert len(figure.layout.shapes) == 3


def test_market_chart_labels_use_correct_axes_and_currency_ticks():
    import pandas as pd
    from obrm.dashboard.app import build_market_chart

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "price_usd": [90_000.0, 91_000.0],
            "fair_value_usd": [80_000.0, 80_500.0],
            "premium_pct": [12.5, 13.0],
            "price_position_risk": [0.5, 0.55],
            "momentum_risk": [0.4, 0.45],
            "volatility_risk": [0.3, 0.35],
            "composite_risk": [0.42, 0.47],
            "confidence_v1": [0.9, 0.9],
            "market_phase": ["Neutral", "Neutral"],
            "decision_label": ["Hold", "Hold"],
            "dca_in_multiplier": [1.0, 1.0],
            "dca_out_pct_weekly": [0.0, 0.0],
            "provider": ["Test", "Test"],
        }
    )
    annotations = [
        ChartAnnotation.create("horizontal_price", 75_000, "Price test"),
        ChartAnnotation.create("horizontal_risk", 0.75, "Risk test"),
    ]
    figure = build_market_chart(frame, annotations)
    labels = {annotation.text: annotation for annotation in figure.layout.annotations}
    assert labels["Price test: $75,000"].yref == "y"
    assert labels["Risk test: 0.75"].yref == "y2"
    assert labels["Risk test: 0.75"].y == 0.75
    assert all(str(value).startswith("$") for value in figure.layout.yaxis.ticktext)
    assert "$50k" in figure.layout.yaxis.ticktext


def test_hidden_annotation_is_not_rendered():
    from dataclasses import replace
    import pandas as pd
    from obrm.dashboard.app import build_market_chart

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "price_usd": [90_000.0, 91_000.0],
            "fair_value_usd": [80_000.0, 80_500.0],
            "premium_pct": [12.5, 13.0],
            "price_position_risk": [0.5, 0.55],
            "momentum_risk": [0.4, 0.45],
            "volatility_risk": [0.3, 0.35],
            "composite_risk": [0.42, 0.47],
            "confidence_v1": [0.9, 0.9],
            "market_phase": ["Neutral", "Neutral"],
            "decision_label": ["Hold", "Hold"],
            "dca_in_multiplier": [1.0, 1.0],
            "dca_out_pct_weekly": [0.0, 0.0],
            "provider": ["Test", "Test"],
        }
    )
    hidden = replace(ChartAnnotation.create("horizontal_risk", 0.75, "Hidden"), visible=False)
    figure = build_market_chart(frame, [hidden])
    assert len(figure.layout.shapes or []) == 0
    assert not any(annotation.text == "Hidden: 0.75" for annotation in figure.layout.annotations or [])
