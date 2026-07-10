"""Market Data Engine."""

import logging
from pathlib import Path

import pandas as pd

from obrm.core.config import AppConfig, load_config
from obrm.core.paths import BTC_PRICE_FILE
from obrm.data.metadata import build_metadata, save_metadata
from obrm.data.providers.registry import build_provider
from obrm.data.storage import load_parquet, save_parquet
from obrm.data.validator import validate_price_data

logger = logging.getLogger(__name__)

BTC_METADATA_FILE = BTC_PRICE_FILE.with_suffix(".metadata.json")


class MarketDataEngine:
    """Load, refresh, validate, and store standardized market data."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()

    def refresh_btc_price_history(self) -> pd.DataFrame:
        """Download BTC history using the configured provider fallback chain."""
        provider_names = (
            self.config.primary_provider,
            *self.config.fallback_providers,
        )
        failures: list[str] = []

        for provider_name in provider_names:
            provider = build_provider(provider_name)

            try:
                logger.info("Trying market data provider: %s", provider.name)
                df = provider.get_btc_daily_price()
                validate_price_data(df)
                save_parquet(df, BTC_PRICE_FILE)

                metadata = build_metadata(df, BTC_PRICE_FILE)
                save_metadata(metadata, BTC_METADATA_FILE)

                logger.info(
                    "Saved %s rows from %s covering %s to %s",
                    len(df),
                    provider.name,
                    df["date"].min().date(),
                    df["date"].max().date(),
                )
                return df
            except Exception as exc:
                logger.warning("%s failed: %s", provider.name, exc)
                failures.append(f"{provider.name}: {exc}")

        raise RuntimeError(
            "Every configured market data provider failed. "
            + " | ".join(failures)
        )

    def get_btc_price_history(self, refresh: bool = False) -> pd.DataFrame:
        """Return cached BTC history, optionally refreshing first."""
        if refresh or not BTC_PRICE_FILE.exists():
            return self.refresh_btc_price_history()

        df = load_parquet(BTC_PRICE_FILE)
        validate_price_data(df)
        return df
