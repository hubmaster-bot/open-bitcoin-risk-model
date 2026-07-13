"""Provider protocol for all future research-data domains."""

from __future__ import annotations

from typing import Protocol

import pandas as pd

from obrm.research_data.models import MetricCapability


class ResearchDataProvider(Protocol):
    name: str

    def discover_asset_metrics(
        self,
        asset: str,
    ) -> tuple[MetricCapability, ...]:
        """Return metrics available for one asset."""

    def fetch_asset_metrics(
        self,
        asset: str,
        metrics: tuple[str, ...],
        *,
        frequency: str = "1d",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> pd.DataFrame:
        """Return standardized time-series metrics."""
