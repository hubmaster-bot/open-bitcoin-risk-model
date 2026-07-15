"""Evidence coverage and health calculations."""

from __future__ import annotations

from dataclasses import dataclass

from obrm.evidence.models import EVIDENCE_STATUS_VALIDATED, EvidenceItem


@dataclass(frozen=True)
class EvidenceCoverage:
    scope: str
    validated: int
    total: int
    ratio: float


def calculate_coverage(
    evidence: tuple[EvidenceItem, ...],
    *,
    scope: str = "Overall",
) -> EvidenceCoverage:
    """Calculate validated evidence coverage for a collection."""
    total = len(evidence)
    validated = sum(
        item.status == EVIDENCE_STATUS_VALIDATED
        for item in evidence
    )
    ratio = validated / total if total else 0.0
    return EvidenceCoverage(
        scope=scope,
        validated=validated,
        total=total,
        ratio=ratio,
    )


def coverage_by_domain(
    evidence: tuple[EvidenceItem, ...],
) -> tuple[EvidenceCoverage, ...]:
    """Return deterministic per-domain coverage summaries."""
    domains = sorted({item.domain for item in evidence})
    return tuple(
        calculate_coverage(
            tuple(item for item in evidence if item.domain == domain),
            scope=domain,
        )
        for domain in domains
    )


def required_dimension_coverage(
    evidence: tuple[EvidenceItem, ...],
    intended_dimension: str,
) -> EvidenceCoverage:
    """Coverage of required evidence for one intended dimension."""
    selected = tuple(
        item
        for item in evidence
        if item.intended_dimension == intended_dimension
        and item.required_for_dimension
    )
    return calculate_coverage(
        selected,
        scope=intended_dimension,
    )
