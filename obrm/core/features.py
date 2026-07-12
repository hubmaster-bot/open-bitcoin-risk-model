"""Feature registry for OBRM capabilities."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Feature:
    key: str
    name: str
    category: str
    available: bool
    version_added: str
    description: str


FEATURES: tuple[Feature, ...] = (
    Feature("btc_price", "Bitcoin price history", "Research Data", True, "0.2.0",
            "Validated daily BTC/USD price history."),
    Feature("market_data_fusion", "Market data fusion", "Research Data", True, "0.3.4",
            "Combines deep historical coverage with a fresher live source."),
    Feature("research_console", "Research Console", "Presentation", True, "0.3.3",
            "Shows data health, provenance, coverage, and integrity."),
    Feature("log_regression_fair_value", "Log Regression Fair Value", "Analytics", True, "0.4.0",
            "Expanding, no-look-ahead Bitcoin fair-value model."),
    Feature("valuation_risk", "Valuation Risk", "Analytics", True, "0.4.0",
            "Normalized valuation risk derived from trend deviation."),
    Feature("momentum_risk", "Momentum Risk", "Analytics", True, "0.5.0",
            "Momentum risk from medium- and long-term price behaviour."),
    Feature("volatility_risk", "Volatility Risk", "Analytics", True, "0.5.0",
            "Volatility risk from realised volatility and drawdown."),
    Feature("composite_risk", "Composite OBRM Risk", "Analytics", True, "0.5.0",
            "Transparent weighted blend of valuation, momentum, and volatility."),
    Feature("confidence_engine_v1", "Confidence Engine v1", "Decision", True, "0.5.0",
            "Confidence from quality, coverage, agreement, and maturity."),
    Feature("decision_engine_preview", "Decision Engine Preview", "Decision", True, "0.5.0",
            "Preview-only DCA-in, hold, pause, and DCA-out actions."),
    Feature("backtesting_engine", "Backtesting Engine", "Research", True, "0.6.0",
            "Historical comparison of fixed DCA and OBRM dynamic allocation."),
    Feature("walk_forward_validation", "Walk-Forward Validation", "Research", True, "0.7.0",
            "Time-ordered validation using only information available at each date."),
    Feature("portfolio_layer", "Portfolio Layer", "Decision", True, "0.8.0",
            "Personal portfolio inputs, allocation diagnostics, and rebalancing guidance."),
    Feature("capital_recovery", "Capital Recovery Planning", "Decision", True, "0.8.0",
            "Optional DCA-out target for recovering contributed capital."),
    Feature("transaction_cost_model", "Transaction Cost Model", "Research", False, "planned",
            "Fees, spread, slippage, and tax-aware simulation."),
    Feature("onchain_risk", "On-chain Risk", "Analytics", False, "planned",
            "Transparent on-chain component for the composite model."),
)


def available_features() -> tuple[Feature, ...]:
    return tuple(feature for feature in FEATURES if feature.available)


def planned_features() -> tuple[Feature, ...]:
    return tuple(feature for feature in FEATURES if not feature.available)
