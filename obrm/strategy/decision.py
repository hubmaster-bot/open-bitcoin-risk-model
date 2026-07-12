"""Preview-only DCA-in and DCA-out decision rules."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Decision:
    action: str
    label: str
    dca_in_multiplier: float
    dca_out_pct_weekly: float
    explanation: str


def decision_for_risk(
    risk: float | None,
    confidence: float | None,
) -> Decision:
    """Return a preview decision from composite risk and confidence."""
    if risk is None or pd.isna(risk):
        return Decision(
            "unavailable",
            "Model warm-up",
            0.0,
            0.0,
            "Insufficient history for a composite decision.",
        )

    risk_value = min(max(float(risk), 0.0), 1.0)
    confidence_value = 0.0 if confidence is None or pd.isna(confidence) else float(confidence)

    if confidence_value < 0.55:
        return Decision(
            "hold",
            "Low-confidence hold",
            0.0,
            0.0,
            "Signals are not sufficiently reliable for an active recommendation.",
        )

    if risk_value <= 0.20:
        return Decision(
            "dca_in",
            "Aggressive accumulation",
            2.50,
            0.0,
            "Composite risk is in the Deep Value range.",
        )
    if risk_value <= 0.40:
        return Decision(
            "dca_in",
            "Accumulation",
            1.75,
            0.0,
            "Composite risk is favourable for above-normal accumulation.",
        )
    if risk_value <= 0.60:
        return Decision(
            "dca_in",
            "Normal DCA",
            1.00,
            0.0,
            "Composite risk is neutral.",
        )
    if risk_value <= 0.75:
        return Decision(
            "dca_in",
            "Reduced DCA",
            0.50,
            0.0,
            "Composite risk is elevated but not yet in distribution territory.",
        )
    if risk_value <= 0.85:
        return Decision(
            "pause",
            "Pause new DCA",
            0.0,
            0.0,
            "Composite risk is high enough to pause new accumulation.",
        )
    if risk_value <= 0.95:
        return Decision(
            "dca_out",
            "Gradual DCA out",
            0.0,
            0.50,
            "Composite risk is in the Distribution range.",
        )
    return Decision(
        "dca_out",
        "Stronger DCA out",
        0.0,
        1.00,
        "Composite risk is in the Extreme Risk range.",
    )
