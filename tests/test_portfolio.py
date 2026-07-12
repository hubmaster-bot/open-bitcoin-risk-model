"""Tests for the OBRM portfolio layer."""

import pytest

from obrm.portfolio.model import (
    PortfolioInputs,
    portfolio_recommendation,
    portfolio_snapshot,
)


def test_snapshot_calculates_allocation() -> None:
    inputs = PortfolioInputs(
        btc_holdings=1.0,
        cash_available_usd=50000.0,
        normal_weekly_dca_usd=100.0,
        total_contributed_usd=80000.0,
    )

    snapshot = portfolio_snapshot(inputs, 50000.0)

    assert snapshot.total_value_usd == pytest.approx(100000.0)
    assert snapshot.btc_allocation_pct == pytest.approx(50.0)


def test_dca_in_is_limited_by_available_cash() -> None:
    inputs = PortfolioInputs(
        btc_holdings=0.0,
        cash_available_usd=50.0,
        normal_weekly_dca_usd=100.0,
    )
    snapshot = portfolio_snapshot(inputs, 50000.0)

    recommendation = portfolio_recommendation(
        inputs,
        snapshot,
        decision_action="dca_in",
        decision_label="Aggressive accumulation",
        dca_in_multiplier=2.5,
        dca_out_pct_weekly=0.0,
        confidence=0.9,
    )

    assert recommendation.weekly_buy_usd == pytest.approx(50.0)
    assert recommendation.projected_cash_after_action == pytest.approx(0.0)


def test_dca_out_respects_permanent_core() -> None:
    inputs = PortfolioInputs(
        btc_holdings=1.0,
        cash_available_usd=0.0,
        normal_weekly_dca_usd=100.0,
        permanent_core_btc_pct=99.8,
    )
    snapshot = portfolio_snapshot(inputs, 50000.0)

    recommendation = portfolio_recommendation(
        inputs,
        snapshot,
        decision_action="dca_out",
        decision_label="Gradual DCA out",
        dca_in_multiplier=0.0,
        dca_out_pct_weekly=0.5,
        confidence=0.9,
    )

    assert recommendation.projected_btc_after_action >= snapshot.core_btc_floor


def test_low_confidence_blocks_transaction() -> None:
    inputs = PortfolioInputs(
        btc_holdings=1.0,
        cash_available_usd=1000.0,
        normal_weekly_dca_usd=100.0,
    )
    snapshot = portfolio_snapshot(inputs, 50000.0)

    recommendation = portfolio_recommendation(
        inputs,
        snapshot,
        decision_action="dca_out",
        decision_label="Distribution",
        dca_in_multiplier=0.0,
        dca_out_pct_weekly=1.0,
        confidence=0.4,
    )

    assert recommendation.action == "hold"
    assert recommendation.weekly_sell_btc == 0.0
