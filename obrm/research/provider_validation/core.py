"""Multi-provider equivalence and validation for realized capital-flow evidence.

The module never assumes similarly named metrics are equivalent. Each provider
series must be accompanied by an explicit mapping to a canonical metric kind,
unit, direction and transformation. Reports are research-only and cannot alter
Composite Risk.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

SUPPORTED_PROVIDERS = frozenset({"coin_metrics", "glassnode", "cryptoquant", "coingecko"})


@dataclass(frozen=True)
class ProviderMetricMapping:
    provider: str
    provider_metric: str
    canonical_metric: str
    unit: str
    positive_direction: str
    transformation: str = "identity"
    definition: str = ""
    source_url: str | None = None
    access_tier: str = "unknown"

    def validate(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {self.provider}")
        if self.positive_direction not in {"inflow", "outflow"}:
            raise ValueError("positive_direction must be 'inflow' or 'outflow'")
        if self.transformation not in {"identity", "diff", "pct_change", "negate"}:
            raise ValueError(f"Unsupported transformation: {self.transformation}")
        for name in ("provider_metric", "canonical_metric", "unit"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"Provider mapping requires {name}")


@dataclass(frozen=True)
class ValidationThresholds:
    minimum_overlap_days: int = 365
    minimum_coverage: float = 0.80
    minimum_pearson: float = 0.70
    minimum_spearman: float = 0.70
    maximum_normalized_mae: float = 0.50
    maximum_direction_disagreement: float = 0.25


@dataclass(frozen=True)
class PairwiseValidation:
    provider_a: str
    provider_b: str
    overlap_days: int
    coverage_ratio: float
    pearson: float | None
    spearman: float | None
    normalized_mae: float | None
    direction_disagreement: float | None
    status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class MultiProviderValidationReport:
    canonical_metric: str
    providers: tuple[str, ...]
    pairwise: tuple[PairwiseValidation, ...]
    overall_status: str
    generated_from_hash: str


def canonicalize_provider_series(raw: pd.DataFrame, mapping: ProviderMetricMapping,
                                 *, date_column: str = "date", value_column: str = "value") -> pd.DataFrame:
    mapping.validate()
    missing = {date_column, value_column} - set(raw.columns)
    if missing:
        raise ValueError("Provider data missing columns: " + ", ".join(sorted(missing)))
    frame = pd.DataFrame({
        "date": pd.to_datetime(raw[date_column], errors="coerce", utc=True).dt.tz_convert(None).dt.normalize(),
        "value": pd.to_numeric(raw[value_column], errors="coerce"),
    }).replace([np.inf, -np.inf], np.nan).dropna().sort_values("date")
    frame = frame.drop_duplicates("date", keep="last").reset_index(drop=True)
    if frame.empty:
        raise ValueError("Provider series contains no usable observations")
    if mapping.transformation == "diff":
        frame["value"] = frame["value"].diff()
    elif mapping.transformation == "pct_change":
        frame["value"] = frame["value"].pct_change(fill_method=None)
    elif mapping.transformation == "negate":
        frame["value"] = -frame["value"]
    frame = frame.dropna(subset=["value"]).reset_index(drop=True)
    if mapping.positive_direction == "outflow":
        frame["canonical_value"] = -frame["value"]
    else:
        frame["canonical_value"] = frame["value"]
    frame["provider"] = mapping.provider
    frame["provider_metric"] = mapping.provider_metric
    frame["canonical_metric"] = mapping.canonical_metric
    frame["unit"] = mapping.unit
    return frame


def _safe_corr(a: pd.Series, b: pd.Series, method: str) -> float | None:
    if len(a) < 2 or a.nunique() < 2 or b.nunique() < 2:
        return None
    value = a.corr(b, method=method)
    return None if pd.isna(value) else float(value)


def _normalized_mae(a: pd.Series, b: pd.Series) -> float | None:
    scale = float(pd.concat([a.abs(), b.abs()]).median())
    if not np.isfinite(scale) or scale == 0:
        scale = float(pd.concat([a, b]).std())
    if not np.isfinite(scale) or scale == 0:
        return None
    return float((a - b).abs().mean() / scale)


def compare_provider_pair(a: pd.DataFrame, b: pd.DataFrame,
                          thresholds: ValidationThresholds | None = None) -> PairwiseValidation:
    cfg = thresholds or ValidationThresholds()
    required = {"date", "canonical_value", "provider", "canonical_metric", "unit"}
    for frame in (a, b):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError("Canonical provider frame missing: " + ", ".join(sorted(missing)))
    if a["canonical_metric"].iloc[0] != b["canonical_metric"].iloc[0]:
        raise ValueError("Cannot compare different canonical metrics")
    if a["unit"].iloc[0] != b["unit"].iloc[0]:
        raise ValueError("Cannot compare provider series with different units")
    merged = a[["date", "canonical_value"]].merge(
        b[["date", "canonical_value"]], on="date", how="inner", suffixes=("_a", "_b")
    ).dropna()
    overlap = len(merged)
    union_days = len(set(a["date"]) | set(b["date"]))
    coverage = float(overlap / union_days) if union_days else 0.0
    pearson = _safe_corr(merged["canonical_value_a"], merged["canonical_value_b"], "pearson")
    spearman = _safe_corr(merged["canonical_value_a"], merged["canonical_value_b"], "spearman")
    nmae = _normalized_mae(merged["canonical_value_a"], merged["canonical_value_b"])
    if overlap:
        sa = np.sign(merged["canonical_value_a"].diff())
        sb = np.sign(merged["canonical_value_b"].diff())
        valid = sa.notna() & sb.notna()
        disagreement = float((sa[valid] != sb[valid]).mean()) if valid.any() else None
    else:
        disagreement = None
    reasons: list[str] = []
    if overlap < cfg.minimum_overlap_days: reasons.append("insufficient overlap")
    if coverage < cfg.minimum_coverage: reasons.append("insufficient coverage")
    if pearson is None or pearson < cfg.minimum_pearson: reasons.append("pearson below threshold")
    if spearman is None or spearman < cfg.minimum_spearman: reasons.append("spearman below threshold")
    if nmae is None or nmae > cfg.maximum_normalized_mae: reasons.append("normalized MAE above threshold")
    if disagreement is None or disagreement > cfg.maximum_direction_disagreement: reasons.append("direction disagreement above threshold")
    return PairwiseValidation(
        str(a["provider"].iloc[0]), str(b["provider"].iloc[0]), overlap, coverage,
        pearson, spearman, nmae, disagreement, "pass" if not reasons else "fail", tuple(reasons)
    )


def build_multi_provider_report(frames: dict[str, pd.DataFrame],
                                thresholds: ValidationThresholds | None = None) -> MultiProviderValidationReport:
    if len(frames) < 2:
        raise ValueError("Multi-provider validation requires at least two providers")
    metrics = {str(frame["canonical_metric"].iloc[0]) for frame in frames.values()}
    if len(metrics) != 1:
        raise ValueError("All provider frames must map to one canonical metric")
    pairwise = tuple(compare_provider_pair(frames[a], frames[b], thresholds)
                     for a, b in combinations(sorted(frames), 2))
    payload = pd.concat([frames[k].assign(_key=k) for k in sorted(frames)], ignore_index=True)
    digest = hashlib.sha256(payload.to_csv(index=False).encode("utf-8")).hexdigest()
    overall = "pass" if pairwise and all(p.status == "pass" for p in pairwise) else "fail"
    return MultiProviderValidationReport(next(iter(metrics)), tuple(sorted(frames)), pairwise, overall, digest)


def report_frame(report: MultiProviderValidationReport) -> pd.DataFrame:
    return pd.DataFrame([asdict(item) for item in report.pairwise])


def save_report(report: MultiProviderValidationReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")


def load_report(path: Path) -> MultiProviderValidationReport:
    data = json.loads(path.read_text(encoding="utf-8"))
    pairs = tuple(PairwiseValidation(**{**p, "reasons": tuple(p["reasons"])}) for p in data["pairwise"])
    return MultiProviderValidationReport(
        data["canonical_metric"], tuple(data["providers"]), pairs,
        data["overall_status"], data["generated_from_hash"]
    )
