"""Tests for Evidence Registry lookup and provider ordering."""

import pytest

from obrm.evidence.service import evidence_by_key, mappings_for_evidence


def test_evidence_lookup_returns_registered_item() -> None:
    item = evidence_by_key("realized_valuation")
    assert item.display_name == "Realized Valuation"


def test_unknown_evidence_key_is_rejected() -> None:
    with pytest.raises(KeyError):
        evidence_by_key("unknown")


def test_provider_mappings_are_ordered_by_priority() -> None:
    mappings = mappings_for_evidence("realized_capital_flow")
    priorities = [mapping.priority for mapping in mappings]
    assert priorities == sorted(priorities)
