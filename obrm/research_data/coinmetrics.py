"""Coin Metrics Community research-data provider.

Catalogue discovery uses ``catalog-all/assets`` because that endpoint returns
asset records with their supported metrics and coverage. The provider first
tries an asset-filtered request and falls back to the unfiltered catalogue when
the Community deployment rejects the filter.
"""

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
    timeseries_page_size = 10000

    def __init__(
        self,
        *,
        timeout_seconds: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.session = session or requests.Session()
        self.session.headers.update(
            {"User-Agent": "OBRM/0.9.1.3 research-data-client"}
        )

    def _request_json(
        self,
        url: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout_seconds,
        )

        status_code = int(getattr(response, "status_code", 200))
        if status_code >= 400:
            body = str(getattr(response, "text", ""))[:1000].strip()
            reason = str(getattr(response, "reason", "request failed"))
            raise requests.HTTPError(
                f"{status_code} error from Coin Metrics: "
                f"{body or reason}",
                response=response,
            )

        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Coin Metrics returned a non-object JSON payload.")
        return payload

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request_json(
            f"{self.base_url}/{path.lstrip('/')}",
            params=params,
        )

    def _paged_get(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        next_page_url: str | None = None

        while True:
            payload = (
                self._request_json(next_page_url)
                if next_page_url
                else self._get(path, params=params)
            )

            data = payload.get("data", [])
            if not isinstance(data, list):
                raise ValueError("Coin Metrics response data must be a list.")

            records.extend(item for item in data if isinstance(item, dict))
            raw_next = payload.get("next_page_url")
            next_page_url = str(raw_next) if raw_next else None

            if not next_page_url:
                break

        return records

    def discover_asset_metrics(
        self,
        asset: str,
    ) -> tuple[MetricCapability, ...]:
        """Discover Community metrics and coverage for one asset."""
        requested_asset = asset.strip().lower()
        if not requested_asset:
            raise ValueError("Asset must not be empty.")

        try:
            records = self._paged_get(
                "catalog-all/assets",
                params={"assets": requested_asset},
            )
        except requests.HTTPError as exc:
            response = exc.response
            if response is None or int(getattr(response, "status_code", 0)) != 400:
                raise
            records = self._paged_get("catalog-all/assets")

        capabilities: list[MetricCapability] = []

        for record in records:
            record_asset = str(record.get("asset", "")).strip().lower()
            if record_asset != requested_asset:
                continue

            metrics = record.get("metrics", [])
            if not isinstance(metrics, list):
                continue

            for metric in metrics:
                capability = _capability_from_catalog_metric(
                    provider=self.name,
                    asset=record_asset,
                    metric=metric,
                )
                if capability is not None:
                    capabilities.append(capability)

        if not capabilities:
            raise ValueError(
                "Coin Metrics returned the asset catalogue, but no supported "
                f"metrics were found for '{requested_asset}'."
            )

        unique = {
            (item.asset, item.metric): item
            for item in capabilities
        }
        return tuple(sorted(unique.values(), key=lambda item: item.metric))

    def fetch_asset_metrics(
        self,
        asset: str,
        metrics: tuple[str, ...],
        *,
        frequency: str = "1d",
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> pd.DataFrame:
        """Fetch and standardise Coin Metrics asset metrics."""
        requested_asset = asset.strip().lower()
        if not requested_asset:
            raise ValueError("Asset must not be empty.")
        if not metrics:
            raise ValueError("At least one metric must be requested.")

        params: dict[str, Any] = {
            "assets": requested_asset,
            "metrics": ",".join(metrics),
            "frequency": frequency,
            "page_size": self.timeseries_page_size,
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        records = self._paged_get(
            "timeseries/asset-metrics",
            params=params,
        )

        if not records:
            raise ValueError(
                f"Coin Metrics returned no data for {requested_asset}: {metrics}."
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
        frame["asset"] = requested_asset
        output_columns.extend(["provider", "asset"])

        return (
            frame[output_columns]
            .dropna(subset=["date"])
            .sort_values("date")
            .drop_duplicates(subset=["date"], keep="last")
            .reset_index(drop=True)
        )

    @staticmethod
    def capability_as_dict(
        capability: MetricCapability,
    ) -> dict[str, Any]:
        return asdict(capability)


def _capability_from_catalog_metric(
    *,
    provider: str,
    asset: str,
    metric: object,
) -> MetricCapability | None:
    """Parse either string or object metric representations."""
    if isinstance(metric, str):
        name = metric.strip()
        if not name:
            return None
        return MetricCapability(
            provider=provider,
            asset=asset,
            metric=name,
            frequencies=(),
            min_time=None,
            max_time=None,
            community_available=True,
            description=None,
        )

    if not isinstance(metric, dict):
        return None

    name = str(
        metric.get("metric")
        or metric.get("name")
        or ""
    ).strip()
    if not name:
        return None

    return MetricCapability(
        provider=provider,
        asset=asset,
        metric=name,
        frequencies=_normalise_frequencies(
            metric.get("frequencies", [])
        ),
        min_time=_optional_text(metric.get("min_time")),
        max_time=_optional_text(metric.get("max_time")),
        community_available=True,
        description=_optional_text(
            metric.get("description")
            or metric.get("display_name")
        ),
    )


def _normalise_frequencies(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)

    if not isinstance(value, list):
        return ()

    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            frequency = (
                item.get("frequency")
                or item.get("name")
                or item.get("value")
            )
            if frequency:
                result.append(str(frequency))
    return tuple(result)


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
