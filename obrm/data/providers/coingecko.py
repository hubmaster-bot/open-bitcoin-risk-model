import pandas as pd
import yfinance as yf


class CoinGeckoProvider:
    def get_btc_daily_price(self) -> pd.DataFrame:
        ticker = yf.Ticker("BTC-USD")
        df = ticker.history(period="max", interval="1d")

        if df.empty:
            raise ValueError("No BTC price data returned from Yahoo Finance.")

        df = df.reset_index()
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df["price_usd"] = df["Close"]

        df = df[["date", "price_usd"]]
        df = df.dropna()
        df = df.drop_duplicates(subset="date")
        df = df.sort_values("date").reset_index(drop=True)

        return df