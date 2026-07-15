"""Tests for missing on-chain evidence registry."""

from obrm.research_data.provider_gaps import ONCHAIN_PROVIDER_GAPS


def test_expected_onchain_provider_gaps_are_recorded() -> None:
    categories = {
        item.evidence_category
        for item in ONCHAIN_PROVIDER_GAPS
    }
    assert categories == {
        "Holder Behaviour",
        "Realized Capital Flow",
    }


def test_every_gap_has_a_fallback_path() -> None:
    for gap in ONCHAIN_PROVIDER_GAPS:
        assert gap.preferred_fallback
