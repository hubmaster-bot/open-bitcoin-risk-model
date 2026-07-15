"""Paths for model-promotion decisions."""

from obrm.core.paths import DATA_DIR


VALIDATION_DATA_DIR = DATA_DIR / "validation"
ONCHAIN_PROMOTION_DECISION_FILE = (
    VALIDATION_DATA_DIR / "onchain_promotion_decision.json"
)
