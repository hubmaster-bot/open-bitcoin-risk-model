"""On-chain data selection, refresh, and analytics service."""

from __future__ import annotations

import pandas as pd

from obrm.onchain.analytics import calculate_onchain_analytics
from obrm.onchain.registry import MetricResolution, provider_metrics
from obrm.onchain.selection import resolve_catalog_metrics
from obrm.research_data.engine import OnChainDataEngine
from obrm.research_data.storage import load_research_parquet
from obrm.research_data.paths import ONCHAIN_DATA_FILE


def refresh_selected_onchain_data(
    *,
    start_time: str | None = None,
    end_time: str | None = None,
) -> tuple[pd.DataFrame, MetricResolution]:
    """Resolve catalogue metrics, download them, and calculate analytics."""
    resolution = resolve_catalog_metrics()

    if resolution.unresolved_required:
        raise ValueError(
            "Required Coin Metrics inputs were not found in the local "
            "catalogue: " + ", ".join(resolution.unresolved_required)
        )

    raw = OnChainDataEngine().refresh_dataset(
        provider_metrics(resolution),
        asset="btc",
        frequency="1d",
        start_time=start_time,
        end_time=end_time,
    )
    return calculate_onchain_analytics(raw, resolution), resolution


def load_selected_onchain_analytics() -> tuple[pd.DataFrame, MetricResolution]:
    """Load the cached canonical dataset and recalculate research signals."""
    resolution = resolve_catalog_metrics()

    if not ONCHAIN_DATA_FILE.exists():
        raise FileNotFoundError(
            "No selected on-chain dataset exists. Run the v0.9.1 refresh."
        )

    raw = load_research_parquet(ONCHAIN_DATA_FILE)
    return calculate_onchain_analytics(raw, resolution), resolution
