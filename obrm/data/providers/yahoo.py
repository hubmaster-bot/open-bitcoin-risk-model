"""Yahoo Finance market data provider."""

import pandas as pd
import yfinance as yf

from obrm.data.providers.base import MarketDataProvider


class YahooProvider(MarketDataProvider):
    """Fetch daily BTC/USD history from Yahoo Finance."""

    name = "Yahoo Finance"

    def get_btc_daily_price(self) -> pd.DataFrame:
        df = yf.Ticker("BTC-USD").history(period="max", interval="1d")

        if df.empty:
            raise ValueError("No BTC price data returned from Yahoo Finance.")

        df = df.reset_index()
        result = pd.DataFrame(
            {
                "date": pd.to_datetime(df["Date"], utc=True).dt.tz_localize(None).dt.normalize(),
                "price_usd": pd.to_numeric(df["Close"], errors="coerce"),
            }
        )

        result["provider"] = self.name
        return (
            result.dropna(subset=["date", "price_usd"])
            .drop_duplicates(subset="date")
            .sort_values("date")
            .reset_index(drop=True)
        )
