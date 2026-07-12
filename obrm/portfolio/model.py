"""Portfolio inputs, diagnostics, and decision support."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PortfolioInputs:
    btc_holdings: float
    cash_available_usd: float
    normal_weekly_dca_usd: float
    total_contributed_usd: float = 0.0
    permanent_core_btc_pct: float = 70.0
    target_btc_allocation_pct: float = 80.0
    capital_recovery_enabled: bool = False


@dataclass(frozen=True)
class PortfolioSnapshot:
    btc_price_usd: float
    btc_value_usd: float
    cash_value_usd: float
    total_value_usd: float
    btc_allocation_pct: float
    cash_allocation_pct: float
    unrealised_gain_usd: float
    unrecovered_capital_usd: float
    core_btc_floor: float


@dataclass(frozen=True)
class PortfolioRecommendation:
    action: str
    headline: str
    weekly_buy_usd: float
    weekly_sell_btc: float
    weekly_sell_usd: float
    projected_btc_after_action: float
    projected_cash_after_action: float
    explanation: str


def validate_inputs(inputs: PortfolioInputs) -> None:
    if inputs.btc_holdings < 0:
        raise ValueError("BTC holdings cannot be negative.")
    if inputs.cash_available_usd < 0:
        raise ValueError("Cash available cannot be negative.")
    if inputs.normal_weekly_dca_usd < 0:
        raise ValueError("Normal weekly DCA cannot be negative.")
    if inputs.total_contributed_usd < 0:
        raise ValueError("Total contributed cannot be negative.")
    if not 0 <= inputs.permanent_core_btc_pct <= 100:
        raise ValueError("Permanent core BTC percentage must be between 0 and 100.")
    if not 0 <= inputs.target_btc_allocation_pct <= 100:
        raise ValueError("Target BTC allocation percentage must be between 0 and 100.")


def portfolio_snapshot(
    inputs: PortfolioInputs,
    btc_price_usd: float,
) -> PortfolioSnapshot:
    """Calculate current portfolio composition."""
    validate_inputs(inputs)

    if btc_price_usd <= 0:
        raise ValueError("BTC price must be positive.")

    btc_value = inputs.btc_holdings * btc_price_usd
    total_value = btc_value + inputs.cash_available_usd
    btc_allocation = (btc_value / total_value * 100.0) if total_value > 0 else 0.0
    cash_allocation = 100.0 - btc_allocation if total_value > 0 else 0.0
    unrealised_gain = total_value - inputs.total_contributed_usd
    unrecovered = max(inputs.total_contributed_usd - inputs.cash_available_usd, 0.0)
    core_floor = inputs.btc_holdings * (inputs.permanent_core_btc_pct / 100.0)

    return PortfolioSnapshot(
        btc_price_usd=btc_price_usd,
        btc_value_usd=btc_value,
        cash_value_usd=inputs.cash_available_usd,
        total_value_usd=total_value,
        btc_allocation_pct=btc_allocation,
        cash_allocation_pct=cash_allocation,
        unrealised_gain_usd=unrealised_gain,
        unrecovered_capital_usd=unrecovered,
        core_btc_floor=core_floor,
    )


def portfolio_recommendation(
    inputs: PortfolioInputs,
    snapshot: PortfolioSnapshot,
    decision_action: str,
    decision_label: str,
    dca_in_multiplier: float,
    dca_out_pct_weekly: float,
    confidence: float,
) -> PortfolioRecommendation:
    """Translate the generic decision into portfolio-aware guidance."""
    if pd.isna(confidence) or confidence < 0.55:
        return PortfolioRecommendation(
            action="hold",
            headline="Hold due to low confidence",
            weekly_buy_usd=0.0,
            weekly_sell_btc=0.0,
            weekly_sell_usd=0.0,
            projected_btc_after_action=inputs.btc_holdings,
            projected_cash_after_action=inputs.cash_available_usd,
            explanation="Model confidence is below the active-decision threshold.",
        )

    if decision_action == "dca_in":
        requested_buy = inputs.normal_weekly_dca_usd * float(dca_in_multiplier)
        allocation_gap = max(
            inputs.target_btc_allocation_pct - snapshot.btc_allocation_pct,
            0.0,
        )

        if allocation_gap <= 0:
            requested_buy = min(requested_buy, inputs.normal_weekly_dca_usd)

        buy_usd = min(requested_buy, inputs.cash_available_usd)
        btc_bought = buy_usd / snapshot.btc_price_usd if buy_usd > 0 else 0.0

        return PortfolioRecommendation(
            action="dca_in",
            headline=decision_label,
            weekly_buy_usd=buy_usd,
            weekly_sell_btc=0.0,
            weekly_sell_usd=0.0,
            projected_btc_after_action=inputs.btc_holdings + btc_bought,
            projected_cash_after_action=inputs.cash_available_usd - buy_usd,
            explanation=(
                f"Generic model multiplier is {dca_in_multiplier:.2f}×. "
                f"Current BTC allocation is {snapshot.btc_allocation_pct:.1f}% "
                f"versus a {inputs.target_btc_allocation_pct:.1f}% target."
            ),
        )

    if decision_action == "dca_out":
        candidate_sell = inputs.btc_holdings * (float(dca_out_pct_weekly) / 100.0)
        maximum_sell = max(inputs.btc_holdings - snapshot.core_btc_floor, 0.0)
        sell_btc = min(candidate_sell, maximum_sell)

        if inputs.capital_recovery_enabled and snapshot.unrecovered_capital_usd > 0:
            recovery_cap_btc = snapshot.unrecovered_capital_usd / snapshot.btc_price_usd
            sell_btc = min(sell_btc, recovery_cap_btc)

        sell_usd = sell_btc * snapshot.btc_price_usd

        if sell_btc <= 0:
            return PortfolioRecommendation(
                action="hold",
                headline="Core position protected",
                weekly_buy_usd=0.0,
                weekly_sell_btc=0.0,
                weekly_sell_usd=0.0,
                projected_btc_after_action=inputs.btc_holdings,
                projected_cash_after_action=inputs.cash_available_usd,
                explanation="The configured permanent BTC core prevents further selling.",
            )

        return PortfolioRecommendation(
            action="dca_out",
            headline=decision_label,
            weekly_buy_usd=0.0,
            weekly_sell_btc=sell_btc,
            weekly_sell_usd=sell_usd,
            projected_btc_after_action=inputs.btc_holdings - sell_btc,
            projected_cash_after_action=inputs.cash_available_usd + sell_usd,
            explanation=(
                f"Sell rate is {dca_out_pct_weekly:.2f}% of holdings per week, "
                f"subject to a {inputs.permanent_core_btc_pct:.1f}% permanent core."
            ),
        )

    return PortfolioRecommendation(
        action=decision_action,
        headline=decision_label,
        weekly_buy_usd=0.0,
        weekly_sell_btc=0.0,
        weekly_sell_usd=0.0,
        projected_btc_after_action=inputs.btc_holdings,
        projected_cash_after_action=inputs.cash_available_usd,
        explanation="The current generic decision does not require a portfolio transaction.",
    )
