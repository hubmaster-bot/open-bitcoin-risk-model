"""Market-phase labels for normalized OBRM risk."""

import pandas as pd


def market_phase(risk: float | None) -> str:
    if risk is None or pd.isna(risk):
        return "Model warm-up"

    value = min(max(float(risk), 0.0), 1.0)

    if value <= 0.20:
        return "Deep Value"
    if value <= 0.40:
        return "Accumulation"
    if value <= 0.60:
        return "Neutral"
    if value <= 0.75:
        return "Caution"
    if value <= 0.85:
        return "Late Bull"
    if value <= 0.95:
        return "Distribution"
    return "Extreme Risk"
