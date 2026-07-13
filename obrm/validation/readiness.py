"""Evidence-promotion criteria for new Market Dimensions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadinessAssessment:
    coverage_status: str
    separation_status: str
    independence_status: str
    stability_status: str
    overall_status: str
    reasons: tuple[str, ...]


def assess_readiness(
    *,
    evidence_categories_available: int,
    evidence_categories_intended: int,
    bucket_monotonicity_ratio: float | None,
    maximum_existing_dimension_correlation: float | None,
    valid_period_ratio: float,
) -> ReadinessAssessment:
    """Apply transparent provisional promotion rules."""
    reasons: list[str] = []

    coverage_ratio = (
        evidence_categories_available / evidence_categories_intended
        if evidence_categories_intended
        else 0.0
    )

    coverage_status = (
        "pass" if coverage_ratio >= 0.75
        else "partial" if coverage_ratio >= 0.50
        else "fail"
    )
    if coverage_status != "pass":
        reasons.append(
            f"Evidence-category coverage is {coverage_ratio:.0%}; "
            "the provisional promotion threshold is 75%."
        )

    separation_status = (
        "pass"
        if bucket_monotonicity_ratio is not None
        and bucket_monotonicity_ratio >= 0.75
        else "partial"
        if bucket_monotonicity_ratio is not None
        and bucket_monotonicity_ratio >= 0.50
        else "fail"
    )
    if separation_status != "pass":
        reasons.append(
            "Forward-return ordering is not consistently monotonic "
            "across score bands."
        )

    independence_status = (
        "pass"
        if maximum_existing_dimension_correlation is not None
        and abs(maximum_existing_dimension_correlation) <= 0.80
        else "fail"
    )
    if independence_status != "pass":
        reasons.append(
            "The candidate signal is either highly correlated with an "
            "existing dimension or lacks sufficient correlation evidence."
        )

    stability_status = (
        "pass" if valid_period_ratio >= 0.80
        else "partial" if valid_period_ratio >= 0.60
        else "fail"
    )
    if stability_status != "pass":
        reasons.append(
            f"Usable historical coverage is {valid_period_ratio:.0%}; "
            "the provisional threshold is 80%."
        )

    statuses = (
        coverage_status,
        separation_status,
        independence_status,
        stability_status,
    )

    overall_status = (
        "ready"
        if all(status == "pass" for status in statuses)
        else "research only"
        if "fail" not in statuses
        else "not ready"
    )

    if not reasons:
        reasons.append(
            "All provisional evidence-promotion criteria passed."
        )

    return ReadinessAssessment(
        coverage_status=coverage_status,
        separation_status=separation_status,
        independence_status=independence_status,
        stability_status=stability_status,
        overall_status=overall_status,
        reasons=tuple(reasons),
    )
