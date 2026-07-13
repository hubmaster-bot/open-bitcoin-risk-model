"""Shared research-data models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MetricCapability:
    provider: str
    asset: str
    metric: str
    frequencies: tuple[str, ...]
    min_time: str | None
    max_time: str | None
    community_available: bool
    description: str | None = None


@dataclass(frozen=True)
class ResearchDatasetMetadata:
    dataset: str
    provider: str
    asset: str
    metrics: tuple[str, ...]
    frequency: str
    downloaded_at_utc: str
    coverage_start: str
    coverage_end: str
    rows: int
    missing_dates: int
    days_behind_utc: int
    is_stale: bool
    stale_after_days: int
    sha256: str
    source_endpoint: str
    provider_metadata: dict[str, Any]
