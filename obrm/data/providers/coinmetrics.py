"""Coin Metrics community archive provider."""

import pandas as pd

from obrm.data.providers.base import MarketDataProvider


class CoinMetricsProvider(MarketDataProvider):
    """Fetch BTC PriceUSD history from the Coin Metrics community archive."""

    name = "Coin Metrics Community"
    csv_url = "https://raw.githubusercontent.com/coinmetrics/data/master/csv/btc.csv"

    def get_btc_daily_price(self) -> pd.DataFrame:
        df = pd.read_csv(self.csv_url, low_memory=False)

        if "time" not in df.columns or "PriceUSD" not in df.columns:
            raise ValueError(
                "Coin Metrics data is missing required columns: time, PriceUSD."
            )

        result = pd.DataFrame(
            {
                "date": pd.to_datetime(df["time"], utc=True, errors="coerce")
                .dt.tz_localize(None)
                .dt.normalize(),
                "price_usd": pd.to_numeric(df["PriceUSD"], errors="coerce"),
            }
        )
        result["provider"] = self.name

        return (
            result.dropna(subset=["date", "price_usd"])
            .drop_duplicates(subset="date", keep="last")
            .sort_values("date")
            .reset_index(drop=True)
        )
