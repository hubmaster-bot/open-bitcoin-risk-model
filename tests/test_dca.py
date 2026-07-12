"""Tests for Dynamic DCA rules."""

from obrm.strategy.dca import dca_recommendation


def test_low_risk_uses_strong_accumulation_band() -> None:
    result = dca_recommendation(0.10)
    assert result.multiplier == 2.50
    assert result.label == "Strong accumulation"


def test_high_risk_uses_minimal_dca_band() -> None:
    result = dca_recommendation(0.95)
    assert result.multiplier == 0.20
    assert result.label == "Minimal DCA"
