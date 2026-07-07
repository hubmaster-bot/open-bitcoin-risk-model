import pandas as pd


def validate_price_data(df: pd.DataFrame) -> None:
    required_columns = {"date", "price_usd"}

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df.empty:
        raise ValueError("Price data is empty.")

    if df["price_usd"].isna().any():
        raise ValueError("Price data contains missing values.")

    if (df["price_usd"] <= 0).any():
        raise ValueError("Price data contains non-positive prices.")

    if df["date"].duplicated().any():
        raise ValueError("Price data contains duplicate dates.")