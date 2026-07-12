"""Tests for preview DCA-in and DCA-out decisions."""

from obrm.strategy.decision import decision_for_risk


def test_low_risk_recommends_dca_in() -> None:
    decision = decision_for_risk(0.15, 0.90)
    assert decision.action == "dca_in"
    assert decision.dca_in_multiplier == 2.50
    assert decision.dca_out_pct_weekly == 0.0


def test_high_risk_recommends_dca_out() -> None:
    decision = decision_for_risk(0.90, 0.90)
    assert decision.action == "dca_out"
    assert decision.dca_in_multiplier == 0.0
    assert decision.dca_out_pct_weekly == 0.50


def test_low_confidence_blocks_active_action() -> None:
    decision = decision_for_risk(0.95, 0.40)
    assert decision.action == "hold"
