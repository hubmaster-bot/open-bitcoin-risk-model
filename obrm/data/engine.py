"""Market Data Engine."""

import logging

import pandas as pd

from obrm.core.config import AppConfig, load_config
from obrm.core.paths import BTC_PRICE_FILE
from obrm.data.merge import merge_price_history
from obrm.data.metadata import build_metadata, save_metadata
from obrm.data.providers.registry import build_provider
from obrm.data.storage import load_parquet, save_parquet
from obrm.data.validator import validate_price_data

logger = logging.getLogger(__name__)

BTC_METADATA_FILE = BTC_PRICE_FILE.with_suffix(".metadata.json")


class MarketDataEngine:
    """Load, refresh, validate, merge, and store standardized market data."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or load_config()

    def _fetch(self, provider_name: str) -> pd.DataFrame:
        provider = build_provider(provider_name)
        logger.info("Fetching market data from: %s", provider.name)
        df = provider.get_btc_daily_price()
        validate_price_data(df)
        logger.info(
            "%s returned %s rows covering %s to %s",
            provider.name,
            len(df),
            pd.Timestamp(df["date"].min()).date(),
            pd.Timestamp(df["date"].max()).date(),
        )
        return df

    def refresh_btc_price_history(self) -> pd.DataFrame:
        """Create a continuous BTC series from historical and live sources."""
        failures: list[str] = []
        historical: pd.DataFrame | None = None
        live: pd.DataFrame | None = None

        try:
            historical = self._fetch(self.config.primary_provider)
        except Exception as exc:
            logger.warning(
                "Primary historical provider %s failed: %s",
                self.config.primary_provider,
                exc,
            )
            failures.append(f"{self.config.primary_provider}: {exc}")

        try:
            live = self._fetch("yahoo")
        except Exception as exc:
            logger.warning("Preferred live provider Yahoo Finance failed: %s", exc)
            failures.append(f"yahoo: {exc}")

        if historical is not None and live is not None:
            df = merge_price_history(historical, live)
            logger.info(
                "Fused historical and live sources into %s rows covering %s to %s",
                len(df),
                pd.Timestamp(df["date"].min()).date(),
                pd.Timestamp(df["date"].max()).date(),
            )
        elif historical is not None:
            df = historical
        elif live is not None:
            df = live
        else:
            df = self._try_remaining_fallbacks(failures)

        validate_price_data(df)
        save_parquet(df, BTC_PRICE_FILE)

        metadata = build_metadata(df, BTC_PRICE_FILE)
        save_metadata(metadata, BTC_METADATA_FILE)

        if metadata.is_stale:
            logger.warning(
                "Saved dataset is stale: %s days behind UTC today.",
                metadata.days_behind_utc,
            )
        else:
            logger.info(
                "Saved dataset freshness is healthy: %s day(s) behind UTC today.",
                metadata.days_behind_utc,
            )

        return df

    def _try_remaining_fallbacks(self, failures: list[str]) -> pd.DataFrame:
        """Try configured fallbacks after primary and Yahoo have failed."""
        for provider_name in self.config.fallback_providers:
            if provider_name == "yahoo":
                continue

            try:
                return self._fetch(provider_name)
            except Exception as exc:
                logger.warning("Fallback %s failed: %s", provider_name, exc)
                failures.append(f"{provider_name}: {exc}")

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
