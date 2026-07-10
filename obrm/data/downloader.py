"""Backward-compatible BTC downloader."""

from pathlib import Path

from obrm.core.paths import BTC_PRICE_FILE
from obrm.data.engine import MarketDataEngine


def download_btc_history() -> Path:
    """Refresh and store BTC history through the Market Data Engine."""
    MarketDataEngine().refresh_btc_price_history()
    return BTC_PRICE_FILE
