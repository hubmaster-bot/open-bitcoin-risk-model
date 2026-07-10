"""Validation for standardized market data."""

import pandas as pd


def validate_price_data(df: pd.DataFrame) -> None:
    """Validate the standard OBRM BTC daily price schema."""
    required_columns = {"date", "price_usd", "provider"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df.empty:
        raise ValueError("Price data is empty.")
    if df["date"].isna().any():
        raise ValueError("Price data contains missing dates.")
    if df["price_usd"].isna().any():
        raise ValueError("Price data contains missing prices.")
    if (df["price_usd"] <= 0).any():
        raise ValueError("Price data contains non-positive prices.")
    if df["date"].duplicated().any():
        raise ValueError("Price data contains duplicate dates.")
    if not df["date"].is_monotonic_increasing:
        raise ValueError("Price data must be sorted by date.")
