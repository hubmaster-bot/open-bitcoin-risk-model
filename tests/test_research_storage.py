"""Tests for canonical research-data storage metadata."""

from pathlib import Path

import pandas as pd

from obrm.research_data.storage import (
    build_research_metadata,
    save_research_parquet,
)


def test_metadata_contains_provenance_and_hash(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "MetricA": [1.0, 2.0],
            "provider": ["Test", "Test"],
            "asset": ["btc", "btc"],
        }
    )
    path = tmp_path / "dataset.parquet"
    save_research_parquet(frame, path)

    metadata = build_research_metadata(
        frame,
        path,
        dataset="test",
        provider="Test",
        asset="btc",
        metrics=("MetricA",),
        frequency="1d",
        source_endpoint="https://example.test",
    )

    assert metadata.provider == "Test"
    assert metadata.metrics == ("MetricA",)
    assert len(metadata.sha256) == 64
