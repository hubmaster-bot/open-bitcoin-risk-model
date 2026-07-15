"""Provider-neutral Holder Behaviour research pipeline.

The module accepts a daily time series supplied by an approved provider or a
user-controlled CSV. It deliberately separates the logical evidence from the
source and records definition, licence, and provenance metadata alongside the
canonical dataset.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd


METRIC_KIND_DORMANCY = "dormancy"
METRIC_KIND_COIN_DAYS_DESTROYED = "coin_days_destroyed"
METRIC_KIND_LTH_SUPPLY_PCT = "long_term_holder_supply_pct"
METRIC_KIND_DORMANT_SUPPLY_PCT = "dormant_supply_pct"
METRIC_KIND_CUSTOM_DISTRIBUTION = "custom_distribution"

VALID_METRIC_KINDS: frozenset[str] = frozenset(
    {
        METRIC_KIND_DORMANCY,
        METRIC_KIND_COIN_DAYS_DESTROYED,
        METRIC_KIND_LTH_SUPPLY_PCT,
        METRIC_KIND_DORMANT_SUPPLY_PCT,
        METRIC_KIND_CUSTOM_DISTRIBUTION,
    }
)

HIGHER_MEANS_DISTRIBUTION: frozenset[str] = frozenset(
    {
        METRIC_KIND_DORMANCY,
        METRIC_KIND_COIN_DAYS_DESTROYED,
        METRIC_KIND_CUSTOM_DISTRIBUTION,
    }
)

HIGHER_MEANS_CONVICTION: frozenset[str] = frozenset(
    {
        METRIC_KIND_LTH_SUPPLY_PCT,
        METRIC_KIND_DORMANT_SUPPLY_PCT,
    }
)


@dataclass(frozen=True)
class HolderBehaviourMetadata:
    provider: str
    provider_metric: str
    metric_kind: str
    definition: str
    licence_note: str
    source_url: str | None
    imported_at_utc: str
    coverage_start: str
    coverage_end: str
    rows: int
    missing_dates: int
    sha256: str


@dataclass(frozen=True)
class HolderBehaviourConfig:
    percentile_min_periods: int = 365
    smoothing_days: int = 30
    change_days: int = 90


def prepare_holder_behaviour_frame(
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
) -> pd.DataFrame:
    """Normalize a provider or CSV dataset into the canonical schema."""
    if metric_kind not in VALID_METRIC_KINDS:
        raise ValueError(f"Unsupported holder-behaviour metric kind: {metric_kind}")

    required_text = {
        "provider": provider,
        "provider_metric": provider_metric,
        "definition": definition,
        "licence_note": licence_note,
    }
    missing_text = [name for name, value in required_text.items() if not value.strip()]
    if missing_text:
        raise ValueError(
            "Holder-behaviour provenance is incomplete: " + ", ".join(missing_text)
        )

    missing_columns = {date_column, value_column} - set(raw.columns)
    if missing_columns:
        raise ValueError(
            "Input data is missing columns: " + ", ".join(sorted(missing_columns))
        )

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(raw[date_column], errors="coerce", utc=True)
            .dt.tz_convert(None)
            .dt.normalize(),
            "holder_metric_value": pd.to_numeric(raw[value_column], errors="coerce"),
        }
    )
    frame = frame.dropna(subset=["date", "holder_metric_value"])
    frame = frame.sort_values("date").drop_duplicates("date", keep="last")
    frame = frame.reset_index(drop=True)

    if frame.empty:
        raise ValueError("Holder-behaviour input contains no usable observations.")
    if (frame["holder_metric_value"] < 0).any():
        raise ValueError("Holder-behaviour values must be non-negative.")
    if frame["date"].max() > pd.Timestamp.now(tz="UTC").tz_localize(None).normalize():
        raise ValueError("Holder-behaviour input contains future dates.")

    frame["provider"] = provider.strip()
    frame["provider_metric"] = provider_metric.strip()
    frame["metric_kind"] = metric_kind
    frame["definition"] = definition.strip()
    frame["licence_note"] = licence_note.strip()
    frame["source_url"] = (source_url or "").strip()
    return frame


def validate_holder_behaviour_frame(
    frame: pd.DataFrame,
    *,
    minimum_rows: int = 365,
) -> None:
    required = {
        "date",
        "holder_metric_value",
        "provider",
        "provider_metric",
        "metric_kind",
        "definition",
        "licence_note",
        "source_url",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            "Canonical holder-behaviour data is missing columns: "
            + ", ".join(sorted(missing))
        )
    if len(frame) < minimum_rows:
        raise ValueError(
            f"Holder-behaviour research requires at least {minimum_rows} daily rows."
        )
    if frame["date"].duplicated().any():
        raise ValueError("Holder-behaviour data contains duplicate dates.")
    if not frame["date"].is_monotonic_increasing:
        raise ValueError("Holder-behaviour dates must be sorted.")
    if frame["metric_kind"].nunique() != 1:
        raise ValueError("One canonical dataset may contain only one metric kind.")
    if frame["metric_kind"].iloc[0] not in VALID_METRIC_KINDS:
        raise ValueError("Canonical holder-behaviour metric kind is invalid.")


def expanding_percentile(series: pd.Series, *, min_periods: int) -> pd.Series:
    """No-look-ahead expanding percentile rank."""
    values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    result = np.full(len(values), np.nan)

    for index, value in enumerate(values):
        history = values[: index + 1]
        valid = history[np.isfinite(history)]
        if len(valid) < min_periods or not np.isfinite(value):
            continue
        result[index] = float(np.mean(valid <= value))

    return pd.Series(result, index=series.index, dtype=float)


def build_holder_behaviour_analytics(
    frame: pd.DataFrame,
    config: HolderBehaviourConfig | None = None,
) -> pd.DataFrame:
    """Build a diagnostic score where higher means greater distribution risk."""
    cfg = config or HolderBehaviourConfig()
    validate_holder_behaviour_frame(frame)

    df = frame.copy().sort_values("date").reset_index(drop=True)
    raw_percentile = expanding_percentile(
        df["holder_metric_value"],
        min_periods=cfg.percentile_min_periods,
    )
    metric_kind = str(df["metric_kind"].iloc[0])

    if metric_kind in HIGHER_MEANS_DISTRIBUTION:
        score = raw_percentile
        direction = "higher values imply more old-coin spending or distribution"
    elif metric_kind in HIGHER_MEANS_CONVICTION:
        score = 1.0 - raw_percentile
        direction = "higher values imply stronger holder conviction"
    else:  # pragma: no cover - safeguarded by validation
        raise ValueError(f"Unsupported metric direction: {metric_kind}")

    df["holder_metric_percentile"] = raw_percentile
    df["holder_metric_change_90d"] = df["holder_metric_value"].pct_change(
        cfg.change_days
    )
    df["holder_behaviour_score_raw"] = score.clip(0.0, 1.0)
    df["holder_behaviour_research_score"] = (
        df["holder_behaviour_score_raw"]
        .rolling(cfg.smoothing_days, min_periods=1)
        .mean()
        .clip(0.0, 1.0)
    )
    df["holder_behaviour_input_coverage"] = df[
        "holder_behaviour_research_score"
    ].notna().astype(float)
    df["score_direction"] = direction
    return df


def missing_calendar_dates(frame: pd.DataFrame) -> int:
    expected = pd.date_range(frame["date"].min(), frame["date"].max(), freq="D")
    return int(expected.difference(pd.DatetimeIndex(frame["date"])).size)


def save_holder_behaviour_dataset(
    frame: pd.DataFrame,
    *,
    data_path: Path,
    metadata_path: Path,
) -> HolderBehaviourMetadata:
    """Persist canonical data and immutable provenance metadata."""
    validate_holder_behaviour_frame(frame)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(data_path, index=False)

    digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
    first = frame.iloc[0]
    metadata = HolderBehaviourMetadata(
        provider=str(first["provider"]),
        provider_metric=str(first["provider_metric"]),
        metric_kind=str(first["metric_kind"]),
        definition=str(first["definition"]),
        licence_note=str(first["licence_note"]),
        source_url=str(first["source_url"]) or None,
        imported_at_utc=datetime.now(timezone.utc).isoformat(),
        coverage_start=pd.Timestamp(frame["date"].min()).date().isoformat(),
        coverage_end=pd.Timestamp(frame["date"].max()).date().isoformat(),
        rows=len(frame),
        missing_dates=missing_calendar_dates(frame),
        sha256=digest,
    )
    metadata_path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")
    return metadata


def load_holder_behaviour_dataset(data_path: Path) -> pd.DataFrame:
    if not data_path.exists():
        raise FileNotFoundError(
            "No canonical Holder Behaviour dataset exists. Import a reviewed CSV first."
        )
    frame = pd.read_parquet(data_path)
    validate_holder_behaviour_frame(frame)
    return frame


def load_holder_behaviour_metadata(metadata_path: Path) -> dict[str, object] | None:
    if not metadata_path.exists():
        return None
    return json.loads(metadata_path.read_text(encoding="utf-8"))
