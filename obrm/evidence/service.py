"""Read-only service layer for the canonical evidence registry."""

from __future__ import annotations

from obrm.evidence.coverage import (
    EvidenceCoverage,
    calculate_coverage,
    coverage_by_domain,
    required_dimension_coverage,
)
from obrm.evidence.models import EvidenceItem, EvidenceProviderMapping
from obrm.evidence.registry import EVIDENCE_REGISTRY, PROVIDER_MAPPINGS


def list_evidence() -> tuple[EvidenceItem, ...]:
    return EVIDENCE_REGISTRY


def list_provider_mappings() -> tuple[EvidenceProviderMapping, ...]:
    return PROVIDER_MAPPINGS


def evidence_by_key(key: str) -> EvidenceItem:
    for item in EVIDENCE_REGISTRY:
        if item.key == key:
            return item
    raise KeyError(f"Unknown evidence key: {key}")


def mappings_for_evidence(
    evidence_key: str,
) -> tuple[EvidenceProviderMapping, ...]:
    evidence_by_key(evidence_key)
    return tuple(
        sorted(
            (
                mapping
                for mapping in PROVIDER_MAPPINGS
                if mapping.evidence_key == evidence_key
            ),
            key=lambda mapping: (mapping.priority, mapping.provider),
        )
    )


def overall_coverage() -> EvidenceCoverage:
    return calculate_coverage(EVIDENCE_REGISTRY)


def domain_coverage() -> tuple[EvidenceCoverage, ...]:
    return coverage_by_domain(EVIDENCE_REGISTRY)


def onchain_required_coverage() -> EvidenceCoverage:
    return required_dimension_coverage(
        EVIDENCE_REGISTRY,
        "On-Chain",
    )
