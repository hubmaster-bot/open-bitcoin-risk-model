"""Application service for the on-chain promotion review."""

from __future__ import annotations

from obrm.validation.promotion import (
    PromotionDecision,
    decide_onchain_promotion,
    save_promotion_decision,
)
from obrm.validation.promotion_paths import (
    ONCHAIN_PROMOTION_DECISION_FILE,
)
from obrm.validation.service import load_onchain_validation_report


def run_onchain_promotion_review() -> PromotionDecision:
    """Run validation, decide promotion, and persist the result."""
    report = load_onchain_validation_report()
    decision = decide_onchain_promotion(report)
    save_promotion_decision(
        decision,
        ONCHAIN_PROMOTION_DECISION_FILE,
    )
    return decision
