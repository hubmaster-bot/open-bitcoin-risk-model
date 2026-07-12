"""Dataset metadata helpers."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

import pandas as pd

from obrm.data.merge import SourceSegment, source_segments


@dataclass(frozen=True)
class DatasetMetadata:
    """Audit metadata for one locally stored dataset."""

    dataset: str
    downloaded_at_utc: str
    coverage_start: str
    coverage_end: str
    rows: int
    sha256: str
    days_behind_utc: int
    is_stale: bool
    stale_after_days: int
    sources: tuple[SourceSegment, ...]


def calculate_sha256(path: Path) -> str:
    """Return the SHA-256 hash for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_metadata(
    df: pd.DataFrame,
    path: Path,
    stale_after_days: int = 2,
) -> DatasetMetadata:
    """Create audit metadata for a standardized BTC price dataset."""
    latest_date = pd.Timestamp(df["date"].max()).date()
    today_utc = datetime.now(timezone.utc).date()
    days_behind = max((today_utc - latest_date).days, 0)

    return DatasetMetadata(
        dataset="btc_daily_price",
        downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
        coverage_start=pd.Timestamp(df["date"].min()).date().isoformat(),
        coverage_end=latest_date.isoformat(),
        rows=len(df),
        sha256=calculate_sha256(path),
        days_behind_utc=days_behind,
        is_stale=days_behind > stale_after_days,
        stale_after_days=stale_after_days,
        sources=source_segments(df),
    )


def save_metadata(metadata: DatasetMetadata, path: Path) -> None:
    """Save metadata as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")
