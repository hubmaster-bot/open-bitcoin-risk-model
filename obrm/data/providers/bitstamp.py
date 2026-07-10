"""Bitstamp market data provider."""

import time

import pandas as pd
import requests

from obrm.data.providers.base import MarketDataProvider


class BitstampProvider(MarketDataProvider):
    """Fetch daily BTC/USD OHLC history from Bitstamp."""

    name = "Bitstamp"
    base_url = "https://www.bitstamp.net/api/v2/ohlc/btcusd/"

    def get_btc_daily_price(self) -> pd.DataFrame:
        rows: list[dict[str, str]] = []
        end: int | None = None

        while True:
            params: dict[str, int] = {"step": 86400, "limit": 1000}
            if end is not None:
                params["end"] = end

            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            batch = response.json().get("data", {}).get("ohlc", [])

            if not batch:
                break

            rows.extend(batch)
            oldest = min(int(item["timestamp"]) for item in batch)

            if end is not None and oldest >= end:
                break

            end = oldest - 1

            if oldest <= 1315872000:
                break

            time.sleep(0.2)

        if not rows:
            raise ValueError("No BTC price data returned from Bitstamp.")

        df = pd.DataFrame(rows)
        result = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    pd.to_numeric(df["timestamp"]), unit="s", utc=True
                ).dt.tz_localize(None).dt.normalize(),
                "price_usd": pd.to_numeric(df["close"], errors="coerce"),
            }
        )

        result["provider"] = self.name
        return (
            result.dropna(subset=["date", "price_usd"])
            .drop_duplicates(subset="date")
            .sort_values("date")
            .reset_index(drop=True)
        )
