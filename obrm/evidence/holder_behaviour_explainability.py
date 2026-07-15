"""Plain-English interpretation for Holder Behaviour research."""

from __future__ import annotations

import pandas as pd


def holder_behaviour_label(score: float | None) -> str:
    if score is None or pd.isna(score):
        return "Unavailable"
    value = min(max(float(score), 0.0), 1.0)
    if value <= 0.20:
        return "Strong conviction"
    if value <= 0.40:
        return "Constructive"
    if value <= 0.60:
        return "Mixed"
    if value <= 0.80:
        return "Distribution rising"
    return "Elevated distribution"


def explain_holder_behaviour_row(row: pd.Series) -> tuple[str, ...]:
    score = row.get("holder_behaviour_research_score")
    metric = row.get("provider_metric", "the imported metric")
    change = row.get("holder_metric_change_90d")

    notes = [
        f"{metric} produces a Holder Behaviour research score of "
        f"{float(score):.2f} ({holder_behaviour_label(score).lower()})."
        if pd.notna(score)
        else "The Holder Behaviour score is not available yet."
    ]
    if pd.notna(change):
        direction = "increased" if float(change) >= 0 else "decreased"
        notes.append(
            f"The raw holder metric has {direction} {abs(float(change)):.1%} over 90 days."
        )
    notes.append(
        "This evidence is research-only and does not affect Composite Risk, "
        "Model Confidence, decisions, or Portfolio Lab."
    )
    return tuple(notes)
