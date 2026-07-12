"""Composite OBRM risk and confidence calculations."""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class CompositeRiskConfig:
    valuation_weight: float = 0.45
    momentum_weight: float = 0.30
    volatility_weight: float = 0.25

    def validate(self) -> None:
        total = (
            self.valuation_weight
            + self.momentum_weight
            + self.volatility_weight
        )
        if not np.isclose(total, 1.0):
            raise ValueError("Composite risk weights must sum to 1.0.")


def calculate_composite_risk(
    analytics: pd.DataFrame,
    config: CompositeRiskConfig | None = None,
) -> pd.DataFrame:
    """Calculate composite risk, component agreement, and confidence v1."""
    cfg = config or CompositeRiskConfig()
    cfg.validate()

    df = analytics.copy()

    components = df[
        [
            "price_position_risk",
            "momentum_risk",
            "volatility_risk",
        ]
    ]

    df["component_coverage"] = components.notna().mean(axis=1)

    weighted_sum = (
        cfg.valuation_weight * df["price_position_risk"].fillna(0.0)
        + cfg.momentum_weight * df["momentum_risk"].fillna(0.0)
        + cfg.volatility_weight * df["volatility_risk"].fillna(0.0)
    )

    available_weight = (
        cfg.valuation_weight * df["price_position_risk"].notna().astype(float)
        + cfg.momentum_weight * df["momentum_risk"].notna().astype(float)
        + cfg.volatility_weight * df["volatility_risk"].notna().astype(float)
    )

    df["composite_risk"] = (
        weighted_sum / available_weight.replace(0.0, np.nan)
    ).clip(0.0, 1.0)

    component_spread = components.max(axis=1) - components.min(axis=1)
    df["component_agreement"] = (1.0 - component_spread).clip(0.0, 1.0)

    model_quality = df["preliminary_confidence"].fillna(0.0)
    data_quality = pd.Series(1.0, index=df.index)

    df["confidence_v1"] = (
        0.35 * model_quality
        + 0.30 * df["component_agreement"].fillna(0.0)
        + 0.20 * df["component_coverage"].fillna(0.0)
        + 0.15 * data_quality
    ).clip(0.0, 1.0)

    return df
