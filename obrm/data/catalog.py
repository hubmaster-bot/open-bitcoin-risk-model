"""Dataset catalogue helpers."""

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(frozen=True)
class SourceStatus:
    """One provider segment in the local dataset."""

    provider: str
    start_date: str
    end_date: str
    rows: int


@dataclass(frozen=True)
class DatasetStatus:
    """Data-health information loaded from dataset metadata."""

    dataset: str
    downloaded_at_utc: str
    coverage_start: str
    coverage_end: str
    rows: int
    sha256: str
    days_behind_utc: int
    is_stale: bool
    stale_after_days: int
    sources: tuple[SourceStatus, ...]


def load_dataset_status(metadata_path: Path) -> DatasetStatus | None:
    """Load dataset metadata when available."""
    if not metadata_path.exists():
        return None

    payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    sources = tuple(SourceStatus(**item) for item in payload.pop("sources", []))
    return DatasetStatus(sources=sources, **payload)
