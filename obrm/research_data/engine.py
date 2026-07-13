"""Canonical research-data engine."""

from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from obrm.research_data.catalog import save_metric_catalog
from obrm.research_data.coinmetrics import CoinMetricsCommunityProvider
from obrm.research_data.models import MetricCapability
from obrm.research_data.paths import (
    ONCHAIN_CATALOG_FILE,
    ONCHAIN_DATA_FILE,
    ONCHAIN_METADATA_FILE,
)
from obrm.research_data.storage import (
    build_research_metadata,
    load_research_parquet,
    save_research_metadata,
    save_research_parquet,
)
from obrm.research_data.validation import validate_research_dataset


class OnChainDataEngine:
    """Discover, fetch, validate, and cache canonical on-chain data."""

    def __init__(
        self,
        provider: CoinMetricsCommunityProvider | None = None,
    ) -> None:
        self.provider = provider or CoinMetricsCommunityProvider()

    def refresh_catalog(
        self,
        asset: str = "btc",
    ) -> tuple[MetricCapability, ...]:
        capabilities = self.provider.discover_asset_metrics(asset)
        save_metric_catalog(capabilities, ONCHAIN_CATALOG_FILE)
        return capabilities

    def refresh_dataset(
        self,
        metrics: tuple[str, ...],
        *,
        asset: str = "btc",
        frequency: str = "1d",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> pd.DataFrame:
        """Download selected metrics after capability review."""
        frame = self.provider.fetch_asset_metrics(
            asset,
            metrics,
            frequency=frequency,
            start_time=start_time,
            end_time=end_time,
        )
        validate_research_dataset(frame, metrics)

        save_research_parquet(frame, ONCHAIN_DATA_FILE)
        metadata = build_research_metadata(
            frame,
            ONCHAIN_DATA_FILE,
            dataset="btc_onchain_daily",
            provider=self.provider.name,
            asset=asset,
            metrics=metrics,
            frequency=frequency,
            source_endpoint=(
                f"{self.provider.base_url}/timeseries/asset-metrics"
            ),
            provider_metadata={
                "catalog_endpoint": (
                    f"{self.provider.base_url}/catalog/asset-metrics"
                ),
                "capabilities_reviewed": True,
            },
        )
        save_research_metadata(metadata, ONCHAIN_METADATA_FILE)
        return frame

    def get_cached_dataset(self) -> pd.DataFrame:
        if not ONCHAIN_DATA_FILE.exists():
            raise FileNotFoundError(
                "No canonical on-chain dataset exists yet. "
                "Review the catalogue before selecting metrics."
            )
        return load_research_parquet(ONCHAIN_DATA_FILE)
