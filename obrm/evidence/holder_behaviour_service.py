"""Application service for Holder Behaviour research."""

from __future__ import annotations

import pandas as pd

from obrm.evidence.holder_behaviour import (
    HolderBehaviourMetadata,
    build_holder_behaviour_analytics,
    load_holder_behaviour_dataset,
    prepare_holder_behaviour_frame,
    save_holder_behaviour_dataset,
)
from obrm.evidence.holder_behaviour_paths import (
    HOLDER_BEHAVIOUR_DATA_FILE,
    HOLDER_BEHAVIOUR_METADATA_FILE,
)


def import_holder_behaviour_csv(
    raw: pd.DataFrame,
    *,
    date_column: str,
    value_column: str,
    provider: str,
    provider_metric: str,
    metric_kind: str,
    definition: str,
    licence_note: str,
    source_url: str | None = None,
) -> tuple[pd.DataFrame, HolderBehaviourMetadata]:
    canonical = prepare_holder_behaviour_frame(
        raw,
        date_column=date_column,
        value_column=value_column,
        provider=provider,
        provider_metric=provider_metric,
        metric_kind=metric_kind,
        definition=definition,
        licence_note=licence_note,
        source_url=source_url,
    )
    metadata = save_holder_behaviour_dataset(
        canonical,
        data_path=HOLDER_BEHAVIOUR_DATA_FILE,
        metadata_path=HOLDER_BEHAVIOUR_METADATA_FILE,
    )
    return build_holder_behaviour_analytics(canonical), metadata


def load_holder_behaviour_analytics() -> pd.DataFrame:
    canonical = load_holder_behaviour_dataset(HOLDER_BEHAVIOUR_DATA_FILE)
    return build_holder_behaviour_analytics(canonical)
