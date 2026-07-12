"""Tests for descriptive OBRM market phases."""

from obrm.analytics.phases import market_phase


def test_market_phase_boundaries() -> None:
    assert market_phase(0.10) == "Deep Value"
    assert market_phase(0.30) == "Accumulation"
    assert market_phase(0.50) == "Neutral"
    assert market_phase(0.70) == "Caution"
    assert market_phase(0.90) == "Distribution"
