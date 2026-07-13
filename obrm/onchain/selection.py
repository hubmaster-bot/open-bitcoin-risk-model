"""Catalogue and validated-availability selection for on-chain metrics."""

from __future__ import annotations

from obrm.onchain.registry import MetricResolution, resolve_metric_specs
from obrm.research_data.availability import (
    STATUS_AVAILABLE,
    load_availability_registry,
)
from obrm.research_data.catalog import load_metric_catalog
from obrm.research_data.models import MetricCapability
from obrm.research_data.paths import (
    ONCHAIN_AVAILABILITY_FILE,
    ONCHAIN_CATALOG_FILE,
)


def load_catalog_capabilities() -> tuple[MetricCapability, ...]:
    payload = load_metric_catalog(ONCHAIN_CATALOG_FILE)
    if payload is None:
        raise FileNotFoundError(
            "Coin Metrics catalogue not found. Refresh it from On-Chain Data."
        )

    return tuple(
        MetricCapability(
            provider=str(item["provider"]),
            asset=str(item["asset"]),
            metric=str(item["metric"]),
            frequencies=tuple(item.get("frequencies", [])),
            min_time=item.get("min_time"),
            max_time=item.get("max_time"),
            community_available=bool(
                item.get("community_available", True)
            ),
            description=item.get("description"),
        )
        for item in payload.get("metrics", [])
    )


def load_validated_capabilities() -> tuple[MetricCapability, ...]:
    """Return only metrics proven downloadable with Community access."""
    capabilities = load_catalog_capabilities()
    registry = load_availability_registry(ONCHAIN_AVAILABILITY_FILE)

    if registry is None:
        raise FileNotFoundError(
            "Validated metric registry not found. Run Community Metric "
            "Validator before refreshing On-Chain Analytics."
        )

    available_names = {
        str(item["metric"])
        for item in registry.get("results", [])
        if item.get("status") == STATUS_AVAILABLE
    }

    return tuple(
        capability
        for capability in capabilities
        if capability.metric in available_names
    )


def resolve_catalog_metrics() -> MetricResolution:
    """Resolve logical analytics only from empirically available metrics."""
    return resolve_metric_specs(load_validated_capabilities())
