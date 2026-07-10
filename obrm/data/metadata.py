"""Dataset metadata helpers."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

import pandas as pd


@dataclass(frozen=True)
class DatasetMetadata:
    dataset: str
    provider: str
    downloaded_at_utc: str
    coverage_start: str
    coverage_end: str
    rows: int
    sha256: str


def calculate_sha256(path: Path) -> str:
    """Return the SHA-256 hash for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_metadata(df: pd.DataFrame, path: Path) -> DatasetMetadata:
    """Create metadata for a standardized BTC price dataset."""
    return DatasetMetadata(
        dataset="btc_daily_price",
        provider=str(df["provider"].iloc[-1]),
        downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
        coverage_start=pd.Timestamp(df["date"].min()).date().isoformat(),
        coverage_end=pd.Timestamp(df["date"].max()).date().isoformat(),
        rows=len(df),
        sha256=calculate_sha256(path),
    )


def save_metadata(metadata: DatasetMetadata, path: Path) -> None:
    """Save metadata as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")
