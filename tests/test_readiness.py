"""Tests for Market Dimension promotion rules."""

from obrm.validation.readiness import assess_readiness


def test_incomplete_evidence_is_not_ready() -> None:
    result = assess_readiness(
        evidence_categories_available=2,
        evidence_categories_intended=4,
        bucket_monotonicity_ratio=1.0,
        maximum_existing_dimension_correlation=0.4,
        valid_period_ratio=0.9,
    )

    assert result.coverage_status == "partial"
    assert result.overall_status == "research only"


def test_all_passing_criteria_are_ready() -> None:
    result = assess_readiness(
        evidence_categories_available=4,
        evidence_categories_intended=4,
        bucket_monotonicity_ratio=0.8,
        maximum_existing_dimension_correlation=0.5,
        valid_period_ratio=0.9,
    )

    assert result.overall_status == "ready"
