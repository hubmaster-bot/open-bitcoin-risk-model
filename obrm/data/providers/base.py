"""Provider interface for market data sources."""

from abc import ABC, abstractmethod

import pandas as pd


class MarketDataProvider(ABC):
    """Common interface implemented by all market data providers."""

    name: str

    @abstractmethod
    def get_btc_daily_price(self) -> pd.DataFrame:
        """Return standardized daily BTC/USD price history."""
        raise NotImplementedError
