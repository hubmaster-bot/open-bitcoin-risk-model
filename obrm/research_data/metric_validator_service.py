"""Service for building the verified Community metric registry."""

from __future__ import annotations

from obrm.research_data.availability import (
    MetricAvailability,
    save_availability_registry,
    validate_capabilities,
)
from obrm.research_data.coinmetrics import CoinMetricsCommunityProvider
from obrm.research_data.paths import ONCHAIN_AVAILABILITY_FILE
from obrm.onchain.selection import load_catalog_capabilities


def refresh_metric_availability(
    *,
    search_terms: tuple[str, ...] = (),
    maximum_metrics: int | None = None,
    probe_start_time: str = "2025-01-01",
) -> tuple[MetricAvailability, ...]:
    capabilities = load_catalog_capabilities()

    if search_terms:
        needles = tuple(term.casefold() for term in search_terms)
        capabilities = tuple(
            item
            for item in capabilities
            if any(
                needle in item.metric.casefold()
                or (
                    item.description
                    and needle in item.description.casefold()
                )
                for needle in needles
            )
        )

    results = validate_capabilities(
        CoinMetricsCommunityProvider(),
        capabilities,
        frequency="1d",
        probe_start_time=probe_start_time,
        maximum_metrics=maximum_metrics,
    )
    save_availability_registry(results, ONCHAIN_AVAILABILITY_FILE)
    return results
