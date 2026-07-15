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
    Feature("composite_risk", "Composite OBRM Risk", "Analytics", True, "0.5.0",
            "Transparent weighted blend of current Market Dimensions."),
    Feature("confidence_engine_v1", "Model Confidence v1", "Decision", True, "0.5.0",
            "Confidence from quality, coverage, agreement, and maturity."),
    Feature("backtesting_engine", "Backtesting Engine", "Research", True, "0.6.0",
            "Historical comparison of fixed DCA and OBRM dynamic allocation."),
    Feature("walk_forward_validation", "Walk-Forward Validation", "Research", True, "0.7.0",
            "Time-ordered validation using later returns only as outcome labels."),
    Feature("portfolio_layer", "Portfolio Layer", "Decision", True, "0.8.0",
            "Portfolio-aware planning and constraints."),
    Feature("model_explainability", "Model Explainability", "Presentation", True, "0.8.5",
            "Market Dimensions, Decision Audit, and progressive disclosure."),
    Feature("research_data_provider_architecture", "Research Data Provider Architecture",
            "Research Data", True, "0.9.0",
            "Vendor-independent provider contract for on-chain, macro, and market-structure data."),
    Feature("coinmetrics_community_provider", "Coin Metrics Community Provider",
            "Research Data", True, "0.9.0",
            "Keyless Coin Metrics Community API v4 adapter and capability discovery."),
    Feature("onchain_canonical_storage", "Canonical On-Chain Storage",
            "Research Data", True, "0.9.0",
            "Validated local Parquet, metadata, provenance, and freshness."),
    Feature("onchain_analytics", "On-Chain Analytics", "Analytics", True, "0.9.1",
            "Validated MVRV and hash-rate research analytics."),
    Feature("onchain_validation", "On-Chain Validation", "Research", True, "0.9.4",
            "Forward-return, redundancy, and promotion-gate analysis."),
    Feature("evidence_registry", "Evidence Registry", "Research", True, "0.10.0",
            "Provider-independent registry of logical market evidence and coverage."),
    Feature("fallback_provider_discovery", "Fallback Provider Discovery",
            "Research Data", True, "0.10.1",
            "Structured candidate review for missing evidence providers."),
    Feature("onchain_market_dimension", "On-Chain Market Dimension", "Analytics", False, "planned",
            "Candidate fourth Market Dimension, subject to stronger evidence coverage."),
    Feature("bitcoin_core_metrics", "Self-Built Bitcoin Core Metrics", "Research Data", False, "v2.0",
            "Locally calculated maximum-transparency network metrics."),
)


def available_features() -> tuple[Feature, ...]:
    return tuple(feature for feature in FEATURES if feature.available)


def planned_features() -> tuple[Feature, ...]:
    return tuple(feature for feature in FEATURES if not feature.available)
