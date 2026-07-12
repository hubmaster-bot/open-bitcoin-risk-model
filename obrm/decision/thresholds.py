"""Public decision-threshold metadata."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DecisionThreshold:
    minimum_risk: float
    maximum_risk: float
    label: str
    action: str
    dca_in_multiplier: float
    dca_out_pct_weekly: float


DECISION_THRESHOLDS: tuple[DecisionThreshold, ...] = (
    DecisionThreshold(0.00, 0.20, "Aggressive accumulation", "DCA in", 2.50, 0.00),
    DecisionThreshold(0.20, 0.40, "Accumulation", "DCA in", 1.75, 0.00),
    DecisionThreshold(0.40, 0.60, "Normal DCA", "DCA in", 1.00, 0.00),
    DecisionThreshold(0.60, 0.75, "Reduced DCA", "DCA in", 0.50, 0.00),
    DecisionThreshold(0.75, 0.85, "Pause new DCA", "Pause", 0.00, 0.00),
    DecisionThreshold(0.85, 0.95, "Gradual DCA out", "DCA out", 0.00, 0.50),
    DecisionThreshold(0.95, 1.00, "Stronger DCA out", "DCA out", 0.00, 1.00),
)
