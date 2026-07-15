"""Tests for Holder Behaviour persistence and metadata."""

from pathlib import Path

import numpy as np
import pandas as pd

from obrm.evidence.holder_behaviour import (
    METRIC_KIND_COIN_DAYS_DESTROYED,
    load_holder_behaviour_metadata,
    prepare_holder_behaviour_frame,
    save_holder_behaviour_dataset,
)


def test_save_dataset_creates_hash_and_metadata(tmp_path: Path) -> None:
    raw = pd.DataFrame(
        {
            "date": pd.date_range("2020-01-01", periods=400, freq="D"),
            "cdd": np.linspace(1.0, 10.0, 400),
        }
    )
    frame = prepare_holder_behaviour_frame(
        raw,
        date_column="date",
        value_column="cdd",
        provider="Research Dataset",
        provider_metric="CDD",
        metric_kind=METRIC_KIND_COIN_DAYS_DESTROYED,
        definition="Coin days destroyed per day.",
        licence_note="Research use permitted.",
        source_url="https://example.test",
    )
    data_path = tmp_path / "holder.parquet"
    metadata_path = tmp_path / "holder.json"
    metadata = save_holder_behaviour_dataset(
        frame,
        data_path=data_path,
        metadata_path=metadata_path,
    )

    loaded = load_holder_behaviour_metadata(metadata_path)
    assert data_path.exists()
    assert len(metadata.sha256) == 64
    assert loaded is not None
    assert loaded["provider_metric"] == "CDD"
