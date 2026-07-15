"""Tests for provider-neutral Holder Behaviour evidence."""

import numpy as np
import pandas as pd
import pytest

from obrm.evidence.holder_behaviour import (
    HolderBehaviourConfig,
    METRIC_KIND_DORMANCY,
    METRIC_KIND_LTH_SUPPLY_PCT,
    build_holder_behaviour_analytics,
    prepare_holder_behaviour_frame,
    validate_holder_behaviour_frame,
)


def _raw(rows: int = 800) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "day": pd.date_range("2020-01-01", periods=rows, freq="D"),
            "value": np.linspace(10.0, 100.0, rows),
        }
    )


def _canonical(metric_kind: str = METRIC_KIND_DORMANCY) -> pd.DataFrame:
    return prepare_holder_behaviour_frame(
        _raw(),
        date_column="day",
        value_column="value",
        provider="Test Provider",
        provider_metric="TestMetric",
        metric_kind=metric_kind,
        definition="A documented test metric.",
        licence_note="Test use permitted.",
    )


def test_prepare_frame_records_provenance() -> None:
    frame = _canonical()
    assert frame.loc[0, "provider"] == "Test Provider"
    assert frame.loc[0, "provider_metric"] == "TestMetric"
    assert frame["date"].is_monotonic_increasing


def test_distribution_metric_score_is_bounded() -> None:
    result = build_holder_behaviour_analytics(
        _canonical(),
        HolderBehaviourConfig(
            percentile_min_periods=50,
            smoothing_days=5,
            change_days=30,
        ),
    )
    score = result["holder_behaviour_research_score"].dropna()
    assert not score.empty
    assert score.between(0.0, 1.0).all()
    assert score.iloc[-1] > 0.9


def test_conviction_metric_inverts_score_direction() -> None:
    result = build_holder_behaviour_analytics(
        _canonical(METRIC_KIND_LTH_SUPPLY_PCT),
        HolderBehaviourConfig(
            percentile_min_periods=50,
            smoothing_days=5,
            change_days=30,
        ),
    )
    score = result["holder_behaviour_research_score"].dropna()
    assert score.iloc[-1] < 0.1


def test_short_dataset_is_rejected() -> None:
    frame = _canonical().head(100)
    with pytest.raises(ValueError, match="at least 365"):
        validate_holder_behaviour_frame(frame)


def test_missing_provenance_is_rejected() -> None:
    with pytest.raises(ValueError, match="provenance"):
        prepare_holder_behaviour_frame(
            _raw(),
            date_column="day",
            value_column="value",
            provider="",
            provider_metric="Metric",
            metric_kind=METRIC_KIND_DORMANCY,
            definition="Definition",
            licence_note="Licence",
        )
