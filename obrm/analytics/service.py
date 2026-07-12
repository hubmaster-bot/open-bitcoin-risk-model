"""Analytics service for dashboard consumers."""

import pandas as pd

from obrm.analytics.composite import calculate_composite_risk
from obrm.analytics.log_regression import calculate_log_regression
from obrm.analytics.momentum import calculate_momentum_risk
from obrm.analytics.phases import market_phase
from obrm.analytics.volatility import calculate_volatility_risk
from obrm.strategy.decision import decision_for_risk


def build_risk_dataset(price_data: pd.DataFrame) -> pd.DataFrame:
    """Return price data enriched with v0.5.0 multi-factor analytics."""
    result = calculate_log_regression(price_data)
    result = calculate_momentum_risk(result)
    result = calculate_volatility_risk(result)
    result = calculate_composite_risk(result)

    result["market_phase"] = result["composite_risk"].map(market_phase)

    decisions = result.apply(
        lambda row: decision_for_risk(
            row["composite_risk"],
            row["confidence_v1"],
        ),
        axis=1,
    )

    result["decision_action"] = decisions.map(lambda item: item.action)
    result["decision_label"] = decisions.map(lambda item: item.label)
    result["dca_in_multiplier"] = decisions.map(
        lambda item: item.dca_in_multiplier
    )
    result["dca_out_pct_weekly"] = decisions.map(
        lambda item: item.dca_out_pct_weekly
    )
    result["decision_explanation"] = decisions.map(
        lambda item: item.explanation
    )
    return result


# Backward-compatible alias used by earlier dashboard code.
def build_price_position_dataset(price_data: pd.DataFrame) -> pd.DataFrame:
    return build_risk_dataset(price_data)
