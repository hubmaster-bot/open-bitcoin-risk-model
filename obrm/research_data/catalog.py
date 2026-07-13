"""Local capability catalogue for external research metrics."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import json

from obrm.research_data.models import MetricCapability


def save_metric_catalog(
    capabilities: tuple[MetricCapability, ...],
    path: Path,
) -> None:
    """Persist provider capability discovery for reproducible review."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "count": len(capabilities),
        "metrics": [asdict(item) for item in capabilities],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_metric_catalog(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def filter_capabilities(
    capabilities: tuple[MetricCapability, ...],
    *,
    frequency: str | None = "1d",
    search: str | None = None,
) -> tuple[MetricCapability, ...]:
    """Filter capabilities without coupling analytics to provider names."""
    result = capabilities

    if frequency:
        result = tuple(
            item
            for item in result
            if not item.frequencies or frequency in item.frequencies
        )

    if search:
        needle = search.casefold()
        result = tuple(
            item
            for item in result
            if needle in item.metric.casefold()
            or (
                item.description is not None
                and needle in item.description.casefold()
            )
        )

    return result
