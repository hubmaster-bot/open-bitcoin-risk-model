"""Tests for the provider-independent Evidence Registry."""

from pathlib import Path

from obrm.evidence.models import (
    EVIDENCE_STATUS_VALIDATED,
    PROVIDER_STATUS_VALIDATED,
    VALID_EVIDENCE_STATUSES,
    VALID_PROVIDER_STATUSES,
)
from obrm.evidence.registry import EVIDENCE_REGISTRY, PROVIDER_MAPPINGS


ROOT = Path(__file__).resolve().parents[1]


def test_evidence_keys_and_names_are_unique() -> None:
    keys = [item.key for item in EVIDENCE_REGISTRY]
    names = [item.display_name for item in EVIDENCE_REGISTRY]

    assert len(keys) == len(set(keys))
    assert len(names) == len(set(names))


def test_evidence_statuses_are_supported() -> None:
    assert all(
        item.status in VALID_EVIDENCE_STATUSES
        for item in EVIDENCE_REGISTRY
    )


def test_provider_mappings_reference_registered_evidence() -> None:
    evidence_keys = {item.key for item in EVIDENCE_REGISTRY}

    assert all(
        mapping.evidence_key in evidence_keys
        for mapping in PROVIDER_MAPPINGS
    )
    assert all(
        mapping.status in VALID_PROVIDER_STATUSES
        for mapping in PROVIDER_MAPPINGS
    )


def test_validated_evidence_has_a_validated_provider() -> None:
    validated_provider_keys = {
        mapping.evidence_key
        for mapping in PROVIDER_MAPPINGS
        if mapping.status == PROVIDER_STATUS_VALIDATED
    }

    for item in EVIDENCE_REGISTRY:
        if item.status == EVIDENCE_STATUS_VALIDATED:
            assert item.key in validated_provider_keys


def test_every_evidence_item_has_existing_documentation() -> None:
    for item in EVIDENCE_REGISTRY:
        assert (ROOT / item.documentation).is_file(), item.key
