"""Tests for evidence coverage calculations."""

import pytest

from obrm.evidence.coverage import calculate_coverage, coverage_by_domain
from obrm.evidence.models import (
    EVIDENCE_STATUS_MISSING,
    EVIDENCE_STATUS_VALIDATED,
    EvidenceItem,
)
from obrm.evidence.service import onchain_required_coverage, overall_coverage


def _item(key: str, status: str, domain: str = "Test") -> EvidenceItem:
    return EvidenceItem(
        key=key,
        display_name=key.title(),
        domain=domain,
        intended_dimension=domain,
        purpose="Test evidence.",
        status=status,
        required_for_dimension=True,
        documentation="docs/handbook/14_Evidence_Registry.md",
    )


def test_coverage_counts_validated_evidence() -> None:
    coverage = calculate_coverage(
        (
            _item("one", EVIDENCE_STATUS_VALIDATED),
            _item("two", EVIDENCE_STATUS_MISSING),
        )
    )

    assert coverage.validated == 1
    assert coverage.total == 2
    assert coverage.ratio == pytest.approx(0.5)


def test_domain_coverage_is_deterministic() -> None:
    coverage = coverage_by_domain(
        (
            _item("a", EVIDENCE_STATUS_VALIDATED, "Zeta"),
            _item("b", EVIDENCE_STATUS_MISSING, "Alpha"),
        )
    )

    assert [item.scope for item in coverage] == ["Alpha", "Zeta"]


def test_seed_registry_has_expected_coverage() -> None:
    assert overall_coverage().validated == 2
    assert overall_coverage().total == 8
    assert onchain_required_coverage().validated == 2
    assert onchain_required_coverage().total == 4
