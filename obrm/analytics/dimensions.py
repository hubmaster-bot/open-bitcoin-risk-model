"""Market-dimension registry and shared explanations."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class MarketDimension:
    key: str
    display_name: str
    weight: float
    score_column: str
    raw_description: str


MARKET_DIMENSIONS: tuple[MarketDimension, ...] = (
    MarketDimension("valuation", "Valuation", 0.45, "price_position_risk",
                    "Price position relative to expanding log-regression fair value."),
    MarketDimension("momentum", "Momentum", 0.30, "momentum_risk",
                    "Medium- and long-term price behaviour."),
    MarketDimension("volatility", "Volatility", 0.25, "volatility_risk",
                    "Realised volatility and drawdown from the all-time high."),
)


def dimension_by_key(key: str) -> MarketDimension:
    for dimension in MARKET_DIMENSIONS:
        if dimension.key == key:
            return dimension
    raise KeyError(f"Unknown market dimension: {key}")


def score_label(score: float | None) -> str:
    if score is None:
        return "Unavailable"
    value = min(max(float(score), 0.0), 1.0)
    if value <= 0.20:
        return "Deep Value"
    if value <= 0.40:
        return "Attractive"
    if value <= 0.60:
        return "Neutral"
    if value <= 0.75:
        return "Elevated"
    if value <= 0.90:
        return "High"
    return "Extreme"


def explain_dimension(
    key: str,
    score: float | None,
    *,
    premium_pct: float | None = None,
    return_30d: float | None = None,
    return_90d: float | None = None,
    realised_volatility_30d: float | None = None,
    drawdown_from_ath: float | None = None,
) -> str:
    label = score_label(score)
    if score is None:
        return "This market dimension is not available for the selected date."

    if key == "valuation":
        if premium_pct is None:
            return f"Valuation conditions are {label.lower()} relative to fair value."
        if premium_pct <= -30:
            return f"Bitcoin is materially below fair value ({premium_pct:+.1f}%)."
        if premium_pct < 0:
            return f"Bitcoin is below fair value ({premium_pct:+.1f}%)."
        if premium_pct < 30:
            return f"Bitcoin is moderately above fair value ({premium_pct:+.1f}%)."
        return f"Bitcoin is materially above fair value ({premium_pct:+.1f}%)."

    if key == "momentum":
        short_text = "unavailable" if return_30d is None else f"{return_30d * 100:+.1f}%"
        medium_text = "unavailable" if return_90d is None else f"{return_90d * 100:+.1f}%"
        tone = (
            "Momentum is subdued or recovering."
            if float(score) <= 0.40
            else "Momentum is positive but not extreme."
            if float(score) <= 0.75
            else "Momentum is historically strong and elevated."
        )
        return f"{tone} The 30-day return is {short_text}; the 90-day return is {medium_text}."

    if key == "volatility":
        volatility_text = (
            "unavailable"
            if realised_volatility_30d is None
            else f"{realised_volatility_30d * 100:.1f}% annualised"
        )
        drawdown_text = (
            "unavailable"
            if drawdown_from_ath is None
            else f"{drawdown_from_ath * 100:.1f}%"
        )
        tone = (
            "Market movement is relatively stable or deeply discounted."
            if float(score) <= 0.40
            else "Volatility conditions are moderate."
            if float(score) <= 0.75
            else "Volatility and price position are elevated."
        )
        return f"{tone} Realised volatility is {volatility_text}; drawdown is {drawdown_text}."

    raise KeyError(f"Unknown market dimension: {key}")
