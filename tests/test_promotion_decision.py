"""Tests for formal Market Dimension promotion decisions."""

from types import SimpleNamespace

from obrm.validation.promotion import (
    PROMOTION_STATUS_PROMOTE,
    PROMOTION_STATUS_REJECT,
    PROMOTION_STATUS_RESEARCH,
    decide_onchain_promotion,
)


def _report(overall: str) -> SimpleNamespace:
    readiness = SimpleNamespace(
        overall_status=overall,
        coverage_status="partial",
        separation_status="pass",
        independence_status="pass",
        stability_status="pass",
        reasons=("Coverage remains incomplete.",),
    )
    return SimpleNamespace(readiness=readiness)


def test_ready_report_produces_promote_decision() -> None:
    decision = decide_onchain_promotion(_report("ready"))
    assert decision.status == PROMOTION_STATUS_PROMOTE
    assert decision.live_model_changed is False


def test_partial_report_stays_research_only() -> None:
    decision = decide_onchain_promotion(_report("research only"))
    assert decision.status == PROMOTION_STATUS_RESEARCH


def test_failed_report_is_not_ready() -> None:
    decision = decide_onchain_promotion(_report("not ready"))
    assert decision.status == PROMOTION_STATUS_REJECT
