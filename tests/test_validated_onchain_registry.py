"""Tests for validated on-chain evidence coverage."""

from obrm.onchain.validated_registry import (
    available_evidence_categories,
    available_evidence_count,
    intended_evidence_count,
)


def test_two_of_four_evidence_categories_are_available() -> None:
    assert intended_evidence_count() == 4
    assert available_evidence_count() == 2


def test_available_categories_have_provider_metrics() -> None:
    for category in available_evidence_categories():
        assert category.provider_metric is not None
