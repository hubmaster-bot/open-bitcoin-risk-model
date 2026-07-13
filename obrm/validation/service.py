"""Application service for the On-Chain Validation Lab."""

from __future__ import annotations

from obrm.analytics.service import build_risk_dataset
from obrm.data.engine import MarketDataEngine
from obrm.onchain.validated_registry import (
    available_evidence_count,
    intended_evidence_count,
)
from obrm.onchain.validated_service import load_validated_onchain_data
from obrm.validation.onchain_validation import (
    OnChainValidationReport,
    build_onchain_validation_report,
)


def load_onchain_validation_report() -> OnChainValidationReport:
    prices = MarketDataEngine().get_btc_price_history()
    market = build_risk_dataset(prices)
    onchain = load_validated_onchain_data()

    return build_onchain_validation_report(
        market,
        onchain,
        evidence_categories_available=available_evidence_count(),
        evidence_categories_intended=intended_evidence_count(),
    )
