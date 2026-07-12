"""Tests for public decision thresholds."""

from obrm.decision.thresholds import DECISION_THRESHOLDS


def test_thresholds_cover_full_risk_range() -> None:
    assert DECISION_THRESHOLDS[0].minimum_risk == 0.0
    assert DECISION_THRESHOLDS[-1].maximum_risk == 1.0


def test_thresholds_are_contiguous() -> None:
    for index in range(len(DECISION_THRESHOLDS) - 1):
        left = DECISION_THRESHOLDS[index]
        right = DECISION_THRESHOLDS[index + 1]

        assert left.maximum_risk == right.minimum_risk