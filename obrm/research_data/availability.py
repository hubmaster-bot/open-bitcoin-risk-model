"""Empirical validation of provider metric availability."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
import time

import pandas as pd
import requests

from obrm.research_data.coinmetrics import CoinMetricsCommunityProvider
from obrm.research_data.models import MetricCapability


@dataclass(frozen=True)
class MetricAvailability:
    provider: str
    asset: str
    metric: str
    frequency: str
    status: str
    observations: int
    first_date: str | None
    last_date: str | None
    tested_at_utc: str
    detail: str


STATUS_AVAILABLE = "available"
STATUS_FORBIDDEN = "forbidden"
STATUS_EMPTY = "empty"
STATUS_ERROR = "error"
STATUS_SKIPPED = "skipped"


def probe_metric(
    provider: CoinMetricsCommunityProvider,
    capability: MetricCapability,
    *,
    frequency: str = "1d",
    probe_start_time: str = "2025-01-01",
    probe_end_time: str | None = None,
) -> MetricAvailability:
    """Attempt a small real download and classify the result."""
    now = datetime.now(timezone.utc).isoformat()

    if capability.frequencies and frequency not in capability.frequencies:
        return MetricAvailability(
            provider=provider.name,
            asset=capability.asset,
            metric=capability.metric,
            frequency=frequency,
            status=STATUS_SKIPPED,
            observations=0,
            first_date=None,
            last_date=None,
            tested_at_utc=now,
            detail=f"Catalogue does not advertise frequency {frequency}.",
        )

    try:
        frame = provider.fetch_asset_metrics(
            capability.asset,
            (capability.metric,),
            frequency=frequency,
            start_time=probe_start_time,
            end_time=probe_end_time,
        )
    except requests.HTTPError as exc:
        response = exc.response
        status_code = int(getattr(response, "status_code", 0))
        text = str(getattr(response, "text", exc))[:1000]

        status = (
            STATUS_FORBIDDEN
            if status_code in {401, 403}
            else STATUS_ERROR
        )
        return MetricAvailability(
            provider=provider.name,
            asset=capability.asset,
            metric=capability.metric,
            frequency=frequency,
            status=status,
            observations=0,
            first_date=None,
            last_date=None,
            tested_at_utc=now,
            detail=f"HTTP {status_code}: {text}",
        )
    except (requests.RequestException, ValueError) as exc:
        detail = str(exc)
        status = (
            STATUS_EMPTY
            if "returned no data" in detail.lower()
            else STATUS_ERROR
        )
        return MetricAvailability(
            provider=provider.name,
            asset=capability.asset,
            metric=capability.metric,
            frequency=frequency,
            status=status,
            observations=0,
            first_date=None,
            last_date=None,
            tested_at_utc=now,
            detail=detail[:1000],
        )

    usable = frame[capability.metric].dropna()
    if usable.empty:
        return MetricAvailability(
            provider=provider.name,
            asset=capability.asset,
            metric=capability.metric,
            frequency=frequency,
            status=STATUS_EMPTY,
            observations=0,
            first_date=None,
            last_date=None,
            tested_at_utc=now,
            detail="Request succeeded but returned no usable values.",
        )

    valid_dates = frame.loc[usable.index, "date"]
    return MetricAvailability(
        provider=provider.name,
        asset=capability.asset,
        metric=capability.metric,
        frequency=frequency,
        status=STATUS_AVAILABLE,
        observations=int(len(usable)),
        first_date=pd.Timestamp(valid_dates.min()).date().isoformat(),
        last_date=pd.Timestamp(valid_dates.max()).date().isoformat(),
        tested_at_utc=now,
        detail="Community API download succeeded.",
    )


def validate_capabilities(
    provider: CoinMetricsCommunityProvider,
    capabilities: tuple[MetricCapability, ...],
    *,
    frequency: str = "1d",
    probe_start_time: str = "2025-01-01",
    probe_end_time: str | None = None,
    delay_seconds: float = 0.7,
    maximum_metrics: int | None = None,
) -> tuple[MetricAvailability, ...]:
    """Probe catalogue metrics sequentially within Community rate limits."""
    selected = capabilities
    if maximum_metrics is not None:
        selected = selected[:maximum_metrics]

    results: list[MetricAvailability] = []
    for index, capability in enumerate(selected):
        results.append(
            probe_metric(
                provider,
                capability,
                frequency=frequency,
                probe_start_time=probe_start_time,
                probe_end_time=probe_end_time,
            )
        )
        if index < len(selected) - 1 and delay_seconds > 0:
            time.sleep(delay_seconds)

    return tuple(results)


def save_availability_registry(
    results: tuple[MetricAvailability, ...],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "available_count": sum(
            item.status == STATUS_AVAILABLE for item in results
        ),
        "forbidden_count": sum(
            item.status == STATUS_FORBIDDEN for item in results
        ),
        "results": [asdict(item) for item in results],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_availability_registry(
    path: Path,
) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
