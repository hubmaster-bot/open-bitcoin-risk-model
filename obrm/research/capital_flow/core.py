"""Provider-neutral Realized Capital Flow research analytics.

v0.10.3 keeps capital-flow evidence isolated from live Market Dimensions.  It
accepts reviewed daily data, records immutable provenance, normalizes multiple
capital-flow metric families, and produces no-look-ahead research features.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import hashlib
import json

import numpy as np
import pandas as pd

METRIC_REALIZED_CAP_GROWTH = "realized_cap_growth"
METRIC_REALIZED_CAP_CHANGE = "realized_cap_change"
METRIC_REALIZED_VALUE_FLOW = "realized_value_flow"
METRIC_CAPITAL_INFLOW = "capital_inflow"
METRIC_CAPITAL_OUTFLOW = "capital_outflow"
METRIC_NET_CAPITAL_FLOW = "net_capital_flow"
METRIC_EXCHANGE_NETFLOW = "exchange_netflow"
METRIC_CUSTOM = "custom_capital_flow"

VALID_METRIC_KINDS = frozenset({
    METRIC_REALIZED_CAP_GROWTH, METRIC_REALIZED_CAP_CHANGE,
    METRIC_REALIZED_VALUE_FLOW, METRIC_CAPITAL_INFLOW, METRIC_CAPITAL_OUTFLOW,
    METRIC_NET_CAPITAL_FLOW, METRIC_EXCHANGE_NETFLOW, METRIC_CUSTOM,
})

# Positive values indicate capital entering/constructive flow for these kinds.
POSITIVE_IS_INFLOW = frozenset({
    METRIC_REALIZED_CAP_GROWTH, METRIC_REALIZED_CAP_CHANGE,
    METRIC_REALIZED_VALUE_FLOW, METRIC_CAPITAL_INFLOW, METRIC_NET_CAPITAL_FLOW,
})
# Positive values indicate capital leaving Bitcoin or sell-side pressure.
POSITIVE_IS_OUTFLOW = frozenset({METRIC_CAPITAL_OUTFLOW, METRIC_EXCHANGE_NETFLOW})


@dataclass(frozen=True)
class CapitalFlowConfig:
    percentile_min_periods: int = 365
    smoothing_days: int = 30
    change_days: int = 90
    yearly_window: int = 365
    acceleration_days: int = 30


@dataclass(frozen=True)
class CapitalFlowMetadata:
    provider: str
    provider_metric: str
    metric_kind: str
    definition: str
    licence_note: str
    source_url: str | None
    custom_positive_direction: str | None
    imported_at_utc: str
    coverage_start: str
    coverage_end: str
    rows: int
    missing_dates: int
    sha256: str


def prepare_capital_flow_frame(
    raw: pd.DataFrame, *, date_column: str, value_column: str,
    provider: str, provider_metric: str, metric_kind: str,
    definition: str, licence_note: str, source_url: str | None = None,
    custom_positive_direction: str | None = None,
) -> pd.DataFrame:
    if metric_kind not in VALID_METRIC_KINDS:
        raise ValueError(f"Unsupported capital-flow metric kind: {metric_kind}")
    required_text = {"provider": provider, "provider_metric": provider_metric,
                     "definition": definition, "licence_note": licence_note}
    missing = [k for k, v in required_text.items() if not str(v).strip()]
    if missing:
        raise ValueError("Capital-flow provenance is incomplete: " + ", ".join(missing))
    if metric_kind == METRIC_CUSTOM and custom_positive_direction not in {"inflow", "outflow"}:
        raise ValueError("Custom capital-flow metrics require positive direction: inflow or outflow.")
    absent = {date_column, value_column} - set(raw.columns)
    if absent:
        raise ValueError("Input data is missing columns: " + ", ".join(sorted(absent)))

    frame = pd.DataFrame({
        "date": pd.to_datetime(raw[date_column], errors="coerce", utc=True)
            .dt.tz_convert(None).dt.normalize(),
        "capital_flow_value": pd.to_numeric(raw[value_column], errors="coerce"),
    }).dropna(subset=["date", "capital_flow_value"])
    frame = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["capital_flow_value"])
    frame = frame.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    if frame.empty:
        raise ValueError("Capital-flow input contains no usable observations.")
    if frame["date"].max() > pd.Timestamp.now(tz="UTC").tz_localize(None).normalize():
        raise ValueError("Capital-flow input contains future dates.")
    # Gross flows and levels cannot be negative; changes and net flows may be signed.
    if metric_kind in {METRIC_CAPITAL_INFLOW, METRIC_CAPITAL_OUTFLOW, METRIC_REALIZED_VALUE_FLOW} \
            and (frame["capital_flow_value"] < 0).any():
        raise ValueError("Gross capital-flow values must be non-negative.")

    frame["provider"] = provider.strip()
    frame["provider_metric"] = provider_metric.strip()
    frame["metric_kind"] = metric_kind
    frame["definition"] = definition.strip()
    frame["licence_note"] = licence_note.strip()
    frame["source_url"] = (source_url or "").strip()
    frame["custom_positive_direction"] = custom_positive_direction or ""
    return frame


def validate_capital_flow_frame(frame: pd.DataFrame, *, minimum_rows: int = 365) -> None:
    required = {"date", "capital_flow_value", "provider", "provider_metric", "metric_kind",
                "definition", "licence_note", "source_url", "custom_positive_direction"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError("Canonical capital-flow data is missing columns: " + ", ".join(sorted(missing)))
    if len(frame) < minimum_rows:
        raise ValueError(f"Capital-flow research requires at least {minimum_rows} daily rows.")
    if frame["date"].duplicated().any() or not frame["date"].is_monotonic_increasing:
        raise ValueError("Capital-flow dates must be unique and sorted.")
    if frame["metric_kind"].nunique() != 1 or frame["metric_kind"].iloc[0] not in VALID_METRIC_KINDS:
        raise ValueError("One canonical dataset must contain one valid capital-flow metric kind.")


def expanding_percentile(series: pd.Series, min_periods: int) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").to_numpy(float)
    out = np.full(len(values), np.nan)
    for i, value in enumerate(values):
        history = values[:i + 1]
        valid = history[np.isfinite(history)]
        if np.isfinite(value) and len(valid) >= min_periods:
            out[i] = float(np.mean(valid <= value))
    return pd.Series(out, index=series.index, dtype=float)


def rolling_percentile(series: pd.Series, window: int, min_periods: int) -> pd.Series:
    return series.rolling(window, min_periods=min_periods).apply(
        lambda x: float(np.mean(np.asarray(x) <= x.iloc[-1])), raw=False
    )


def _positive_is_inflow(frame: pd.DataFrame) -> bool:
    kind = str(frame["metric_kind"].iloc[0])
    if kind in POSITIVE_IS_INFLOW:
        return True
    if kind in POSITIVE_IS_OUTFLOW:
        return False
    return str(frame["custom_positive_direction"].iloc[0]) == "inflow"


def build_capital_flow_analytics(
    frame: pd.DataFrame, config: CapitalFlowConfig | None = None,
    validation_hooks: tuple[Callable[[pd.DataFrame], None], ...] = (),
) -> pd.DataFrame:
    """Create research features. Higher score means stronger net capital inflow."""
    cfg = config or CapitalFlowConfig()
    validate_capital_flow_frame(frame)
    df = frame.copy().sort_values("date").reset_index(drop=True)
    value = df["capital_flow_value"]
    df["capital_flow_percentile_expanding"] = expanding_percentile(value, cfg.percentile_min_periods)
    df["capital_flow_smoothed_30d"] = value.rolling(cfg.smoothing_days, min_periods=1).mean()
    # Difference is valid for signed flows; percentage change is unstable around zero.
    df["capital_flow_change_90d"] = value.diff(cfg.change_days)
    df["capital_flow_percentile_1y"] = rolling_percentile(
        value, cfg.yearly_window, min(cfg.percentile_min_periods, cfg.yearly_window)
    )
    trend_delta = df["capital_flow_smoothed_30d"].diff(cfg.change_days)
    df["capital_flow_trend_direction"] = np.select(
        [trend_delta > 0, trend_delta < 0], ["rising", "falling"], default="flat"
    )
    df["capital_flow_acceleration"] = df["capital_flow_smoothed_30d"].diff(cfg.acceleration_days).diff(cfg.acceleration_days)
    percentile = df["capital_flow_percentile_expanding"]
    score = percentile if _positive_is_inflow(df) else 1.0 - percentile
    df["capital_flow_score_raw"] = score.clip(0.0, 1.0)
    df["capital_flow_research_score"] = df["capital_flow_score_raw"].rolling(
        cfg.smoothing_days, min_periods=1
    ).mean().clip(0.0, 1.0)
    df["capital_flow_input_coverage"] = df["capital_flow_research_score"].notna().astype(float)
    df["score_direction"] = "higher means stronger net capital inflow"
    for hook in validation_hooks:
        hook(df)
    return df


def validation_view(analytics: pd.DataFrame) -> pd.DataFrame:
    """Stable hook surface for later forward-return and multi-provider validation."""
    required = ["date", "capital_flow_research_score", "capital_flow_input_coverage"]
    missing = set(required) - set(analytics.columns)
    if missing:
        raise ValueError("Capital-flow validation view missing: " + ", ".join(sorted(missing)))
    return analytics[required].dropna(subset=["capital_flow_research_score"]).copy()


def missing_calendar_dates(frame: pd.DataFrame) -> int:
    expected = pd.date_range(frame["date"].min(), frame["date"].max(), freq="D")
    return int(expected.difference(pd.DatetimeIndex(frame["date"])).size)


def save_capital_flow_dataset(frame: pd.DataFrame, *, data_path: Path, metadata_path: Path) -> CapitalFlowMetadata:
    validate_capital_flow_frame(frame)
    data_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(data_path, index=False)
    digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
    first = frame.iloc[0]
    meta = CapitalFlowMetadata(
        provider=str(first["provider"]), provider_metric=str(first["provider_metric"]),
        metric_kind=str(first["metric_kind"]), definition=str(first["definition"]),
        licence_note=str(first["licence_note"]), source_url=str(first["source_url"]) or None,
        custom_positive_direction=str(first["custom_positive_direction"]) or None,
        imported_at_utc=datetime.now(timezone.utc).isoformat(),
        coverage_start=pd.Timestamp(frame["date"].min()).date().isoformat(),
        coverage_end=pd.Timestamp(frame["date"].max()).date().isoformat(),
        rows=len(frame), missing_dates=missing_calendar_dates(frame), sha256=digest,
    )
    metadata_path.write_text(json.dumps(asdict(meta), indent=2), encoding="utf-8")
    return meta


def load_capital_flow_dataset(data_path: Path) -> pd.DataFrame:
    if not data_path.exists():
        raise FileNotFoundError("No canonical Realized Capital Flow dataset exists. Import a reviewed CSV first.")
    frame = pd.read_parquet(data_path)
    validate_capital_flow_frame(frame)
    return frame


def verify_dataset_integrity(data_path: Path, metadata_path: Path) -> bool:
    if not data_path.exists() or not metadata_path.exists():
        return False
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    return hashlib.sha256(data_path.read_bytes()).hexdigest() == meta.get("sha256")
