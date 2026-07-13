"""Forward-return labels for historical validation."""

from __future__ import annotations

import pandas as pd


DEFAULT_HORIZONS: tuple[int, ...] = (30, 90, 180, 365, 730)


def add_forward_returns(
    frame: pd.DataFrame,
    *,
    price_column: str = "price_usd",
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
) -> pd.DataFrame:
    """Add future-return labels without feeding them into the model."""
    if "date" not in frame.columns:
        raise ValueError("Validation frame requires a date column.")
    if price_column not in frame.columns:
        raise ValueError(
            f"Validation frame requires price column: {price_column}"
        )

    df = frame.copy().sort_values("date").reset_index(drop=True)
    prices = pd.to_numeric(df[price_column], errors="coerce")

    for horizon in horizons:
        if horizon <= 0:
            raise ValueError("Forward-return horizons must be positive.")
        df[f"forward_return_{horizon}d"] = (
            prices.shift(-horizon) / prices - 1.0
        )

    return df
