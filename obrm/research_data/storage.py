"""Storage and metadata for canonical research datasets."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

import pandas as pd

from obrm.research_data.models import ResearchDatasetMetadata
from obrm.research_data.validation import missing_calendar_dates


def save_research_parquet(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, index=False)


def load_research_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_research_metadata(
    frame: pd.DataFrame,
    path: Path,
    *,
    dataset: str,
    provider: str,
    asset: str,
    metrics: tuple[str, ...],
    frequency: str,
    source_endpoint: str,
    provider_metadata: dict[str, object] | None = None,
    stale_after_days: int = 3,
) -> ResearchDatasetMetadata:
    latest = pd.Timestamp(frame["date"].max()).date()
    today = datetime.now(timezone.utc).date()
    days_behind = max((today - latest).days, 0)

    return ResearchDatasetMetadata(
        dataset=dataset,
        provider=provider,
        asset=asset,
        metrics=metrics,
        frequency=frequency,
        downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
        coverage_start=pd.Timestamp(frame["date"].min()).date().isoformat(),
        coverage_end=latest.isoformat(),
        rows=len(frame),
        missing_dates=missing_calendar_dates(frame),
        days_behind_utc=days_behind,
        is_stale=days_behind > stale_after_days,
        stale_after_days=stale_after_days,
        sha256=file_sha256(path),
        source_endpoint=source_endpoint,
        provider_metadata=dict(provider_metadata or {}),
    )


def save_research_metadata(
    metadata: ResearchDatasetMetadata,
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(metadata), indent=2),
        encoding="utf-8",
    )


def load_research_metadata(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
