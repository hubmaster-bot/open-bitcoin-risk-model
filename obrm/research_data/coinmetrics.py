"""Coin Metrics Community research-data provider."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

import pandas as pd
import requests

from obrm.research_data.models import MetricCapability


class CoinMetricsCommunityProvider:
    """Adapter for the keyless Coin Metrics Community API v4."""

    name = "Coin Metrics Community"
    base_url = "https://community-api.coinmetrics.io/v4"

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.session.headers.update(
            {"User-Agent": "OBRM/0.9.0 research-data-client"}
        )

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self.session.get(
            f"{self.base_url}/{path.lstrip('/')}",
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Coin Metrics returned a non-object JSON payload.")
        return payload

    def discover_asset_metrics(
        self,
        asset: str,
    ) -> tuple[MetricCapability, ...]:
        """Discover Community metrics and coverage for one asset."""
        payload = self._get(
            "catalog/asset-metrics",
            params={"assets": asset, "limit": 10000},
        )
        records = payload.get("data", [])
        capabilities: list[MetricCapability] = []

        for record in records:
            record_asset = str(record.get("asset", asset))
            metrics = record.get("metrics", [])

            for metric in metrics:
                metric_name = str(metric.get("metric", metric.get("name", "")))
                if not metric_name:
                    continue

                frequencies = metric.get("frequencies", [])
                if isinstance(frequencies, str):
                    frequencies = [frequencies]

                capabilities.append(
                    MetricCapability(
                        provider=self.name,
                        asset=record_asset,
                        metric=metric_name,
                        frequencies=tuple(str(item) for item in frequencies),
                        min_time=_optional_text(metric.get("min_time")),
                        max_time=_optional_text(metric.get("max_time")),
                        community_available=True,
                        description=_optional_text(
                            metric.get("description")
                            or metric.get("display_name")
                        ),
                    )
                )

        return tuple(sorted(capabilities, key=lambda item: item.metric))

    def fetch_asset_metrics(
        self,
        asset: str,
        metrics: tuple[str, ...],
        *,
        frequency: str = "1d",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> pd.DataFrame:
        """Fetch standardized Coin Metrics asset metrics."""
        if not metrics:
            raise ValueError("At least one metric must be requested.")

        params: dict[str, Any] = {
            "assets": asset,
            "metrics": ",".join(metrics),
            "frequency": frequency,
            "page_size": 10000,
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        records: list[dict[str, Any]] = []
        next_page_url: str | None = None

        while True:
            if next_page_url:
                response = self.session.get(
                    next_page_url,
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                payload = response.json()
            else:
                payload = self._get("timeseries/asset-metrics", params=params)

            records.extend(payload.get("data", []))
            next_page_url = payload.get("next_page_url")
            if not next_page_url:
                break

        if not records:
            raise ValueError(
                f"Coin Metrics returned no data for {asset}: {metrics}."
            )

        frame = pd.DataFrame(records)
        if "time" not in frame.columns:
            raise ValueError("Coin Metrics response is missing the time field.")

        frame["date"] = pd.to_datetime(
            frame["time"],
            utc=True,
            errors="coerce",
        ).dt.tz_convert(None).dt.normalize()

        output_columns = ["date"]
        for metric in metrics:
            if metric not in frame.columns:
                frame[metric] = pd.NA
            frame[metric] = pd.to_numeric(frame[metric], errors="coerce")
            output_columns.append(metric)

        frame["provider"] = self.name
        frame["asset"] = asset
        output_columns.extend(["provider", "asset"])

        return (
            frame[output_columns]
            .dropna(subset=["date"])
            .sort_values("date")
            .drop_duplicates(subset=["date"], keep="last")
            .reset_index(drop=True)
        )

    @staticmethod
    def capability_as_dict(capability: MetricCapability) -> dict[str, Any]:
        return asdict(capability)


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
