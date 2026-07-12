"""Model Confidence labels and explanations."""

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class ModelConfidenceSnapshot:
    overall: float
    coverage: float
    agreement: float
    data_quality: float
    model_maturity: float


def _bounded(value: object) -> float:
    if value is None or pd.isna(value):
        return 0.0
    return min(max(float(value), 0.0), 1.0)


def build_model_confidence_snapshot(row: pd.Series) -> ModelConfidenceSnapshot:
    return ModelConfidenceSnapshot(
        overall=_bounded(row.get("confidence_v1", 0.0)),
        coverage=_bounded(row.get("component_coverage", 0.0)),
        agreement=_bounded(row.get("component_agreement", 0.0)),
        data_quality=1.0,
        model_maturity=_bounded(row.get("preliminary_confidence", 0.0)),
    )


def confidence_label(value: float) -> str:
    bounded = _bounded(value)
    if bounded < 0.55:
        return "Low"
    if bounded < 0.75:
        return "Moderate"
    if bounded < 0.90:
        return "High"
    return "Very High"


def confidence_explanation(snapshot: ModelConfidenceSnapshot) -> str:
    factors = (
        ("coverage", snapshot.coverage),
        ("agreement", snapshot.agreement),
        ("data quality", snapshot.data_quality),
        ("model maturity", snapshot.model_maturity),
    )
    strongest = max(factors, key=lambda item: item[1])
    weakest = min(factors, key=lambda item: item[1])
    return (
        f"Model Confidence is {confidence_label(snapshot.overall).lower()} "
        f"({snapshot.overall:.0%}). The strongest factor is {strongest[0]} "
        f"({strongest[1]:.0%}); the weakest factor is {weakest[0]} "
        f"({weakest[1]:.0%})."
    )
