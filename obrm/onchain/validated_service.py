"""Service for validated on-chain research analytics."""

from __future__ import annotations

import pandas as pd

from obrm.onchain.validated_analytics import (
    build_validated_onchain_analytics,
)
from obrm.research_data.engine import OnChainDataEngine
from obrm.research_data.paths import ONCHAIN_DATA_FILE
from obrm.research_data.storage import load_research_parquet


VALIDATED_PROVIDER_METRICS: tuple[str, ...] = (
    "CapMVRVCur",
    "HashRate",
)


def refresh_validated_onchain_data(
    *,
    start_time: str | None = None,
    end_time: str | None = None,
) -> pd.DataFrame:
    """Download only empirically validated Community metrics."""
    raw = OnChainDataEngine().refresh_dataset(
        VALIDATED_PROVIDER_METRICS,
        asset="btc",
        frequency="1d",
        start_time=start_time,
        end_time=end_time,
    )
    return build_validated_onchain_analytics(raw)


def load_validated_onchain_data() -> pd.DataFrame:
    """Load cached validated metrics and rebuild research analytics."""
    if not ONCHAIN_DATA_FILE.exists():
        raise FileNotFoundError(
            "No validated on-chain dataset exists. Refresh it from the "
            "Validated On-Chain Research page."
        )

    raw = load_research_parquet(ONCHAIN_DATA_FILE)
    missing = set(VALIDATED_PROVIDER_METRICS) - set(raw.columns)
    if missing:
        raise ValueError(
            "The cached on-chain dataset does not contain the validated "
            "v0.9.3 inputs. Refresh the dataset."
        )
    return build_validated_onchain_analytics(raw)
