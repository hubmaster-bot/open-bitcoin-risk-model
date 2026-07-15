"""Outcome validation and promotion review for capital-flow research evidence.

This module is deliberately isolated from Composite Risk. It evaluates whether a
capital-flow score has useful, stable, no-look-ahead relationships with future
Bitcoin returns and drawdowns, then emits a governance decision only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd

PROMOTE = "promote"
RESEARCH_ONLY = "research_only"
NOT_READY = "not_ready"


@dataclass(frozen=True)
class OutcomeValidationConfig:
    horizons: tuple[int, ...] = (30, 90, 180, 365)
    score_bands: int = 5
    minimum_rows: int = 730
    minimum_band_rows: int = 30
    minimum_train_rows: int = 365
    test_window: int = 180
    minimum_provider_count: int = 2
    minimum_provider_correlation: float = 0.70
    minimum_monotonic_horizons: int = 2
    minimum_stable_windows_ratio: float = 0.60
    maximum_high_risk_drawdown_advantage: float = 0.0


@dataclass(frozen=True)
class HorizonOutcome:
    horizon_days: int
    observations: int
    spearman_score_return: float | None
    high_score_mean_return: float | None
    low_score_mean_return: float | None
    return_spread: float | None
    high_score_mean_drawdown: float | None
    low_score_mean_drawdown: float | None
    drawdown_spread: float | None
    monotonic_return_bands: bool
    status: str


@dataclass(frozen=True)
class WalkForwardOutcome:
    windows: int
    stable_windows: int
    stable_ratio: float
    status: str


@dataclass(frozen=True)
class ProviderRobustness:
    providers: tuple[str, ...]
    pairwise_correlations: tuple[float, ...]
    minimum_correlation: float | None
    status: str


@dataclass(frozen=True)
class CapitalFlowOutcomeReport:
    horizons: tuple[HorizonOutcome, ...]
    walk_forward: WalkForwardOutcome
    provider_robustness: ProviderRobustness
    overall_status: str
    promotion_decision: str
    rationale: tuple[str, ...]
    live_model_changed: bool
    generated_from_hash: str


def _safe_spearman(a: pd.Series, b: pd.Series) -> float | None:
    pair = pd.concat([a, b], axis=1).dropna()
    if len(pair) < 3 or pair.iloc[:, 0].nunique() < 2 or pair.iloc[:, 1].nunique() < 2:
        return None
    value = pair.iloc[:, 0].corr(pair.iloc[:, 1], method="spearman")
    return None if pd.isna(value) else float(value)


def add_future_outcomes(frame: pd.DataFrame, *, price_column: str = "price_usd",
                        horizons: tuple[int, ...] = (30, 90, 180, 365)) -> pd.DataFrame:
    """Add future return and maximum drawdown labels without using future data as features."""
    required = {"date", price_column}
    if missing := required - set(frame.columns):
        raise ValueError("Outcome frame missing: " + ", ".join(sorted(missing)))
    df = frame.copy().sort_values("date").reset_index(drop=True)
    price = pd.to_numeric(df[price_column], errors="coerce")
    for horizon in horizons:
        if horizon <= 0:
            raise ValueError("Outcome horizons must be positive")
        df[f"forward_return_{horizon}d"] = price.shift(-horizon) / price - 1.0
        values = price.to_numpy(float)
        drawdowns = np.full(len(df), np.nan)
        for i in range(0, max(0, len(df) - horizon)):
            start = values[i]
            future = values[i + 1:i + horizon + 1]
            if np.isfinite(start) and len(future) == horizon and np.isfinite(future).all():
                drawdowns[i] = float(np.min(future / start - 1.0))
        df[f"forward_max_drawdown_{horizon}d"] = drawdowns
    return df


def _band_series(score: pd.Series, bands: int) -> pd.Series:
    ranked = score.rank(method="first")
    return pd.qcut(ranked, q=bands, labels=False, duplicates="drop")


def evaluate_horizon(df: pd.DataFrame, horizon: int, cfg: OutcomeValidationConfig) -> HorizonOutcome:
    ret_col = f"forward_return_{horizon}d"
    dd_col = f"forward_max_drawdown_{horizon}d"
    subset = df[["capital_flow_research_score", ret_col, dd_col]].dropna().copy()
    if len(subset) < cfg.minimum_rows:
        return HorizonOutcome(horizon, len(subset), None, None, None, None, None, None, None, False, "insufficient_data")
    subset["band"] = _band_series(subset["capital_flow_research_score"], cfg.score_bands)
    grouped = subset.groupby("band", observed=True)
    returns = grouped[ret_col].mean()
    drawdowns = grouped[dd_col].mean()
    counts = grouped.size()
    valid_bands = len(returns) == cfg.score_bands and bool((counts >= cfg.minimum_band_rows).all())
    low, high = returns.index.min(), returns.index.max()
    high_ret, low_ret = float(returns.loc[high]), float(returns.loc[low])
    high_dd, low_dd = float(drawdowns.loc[high]), float(drawdowns.loc[low])
    monotonic = valid_bands and bool(returns.is_monotonic_increasing)
    status = "pass" if monotonic and high_ret > low_ret and high_dd >= low_dd else "fail"
    return HorizonOutcome(
        horizon, len(subset), _safe_spearman(subset["capital_flow_research_score"], subset[ret_col]),
        high_ret, low_ret, high_ret - low_ret, high_dd, low_dd, high_dd - low_dd,
        monotonic, status,
    )


def evaluate_walk_forward(df: pd.DataFrame, cfg: OutcomeValidationConfig) -> WalkForwardOutcome:
    """Evaluate frozen chronological windows; no random split or future fitting is used."""
    ordered = df.sort_values("date").reset_index(drop=True)
    horizon = min(cfg.horizons)
    ret_col = f"forward_return_{horizon}d"
    windows = stable = 0
    start = cfg.minimum_train_rows
    while start + cfg.test_window <= len(ordered):
        test = ordered.iloc[start:start + cfg.test_window][["capital_flow_research_score", ret_col]].dropna().copy()
        if len(test) >= max(20, cfg.minimum_band_rows * 2):
            test["band"] = _band_series(test["capital_flow_research_score"], min(3, cfg.score_bands))
            means = test.groupby("band", observed=True)[ret_col].mean()
            windows += 1
            if len(means) >= 2 and means.iloc[-1] > means.iloc[0]:
                stable += 1
        start += cfg.test_window
    ratio = float(stable / windows) if windows else 0.0
    return WalkForwardOutcome(windows, stable, ratio, "pass" if windows and ratio >= cfg.minimum_stable_windows_ratio else "fail")


def evaluate_provider_robustness(provider_scores: dict[str, pd.DataFrame], cfg: OutcomeValidationConfig) -> ProviderRobustness:
    if len(provider_scores) < cfg.minimum_provider_count:
        return ProviderRobustness(tuple(sorted(provider_scores)), (), None, "insufficient_data")
    merged: pd.DataFrame | None = None
    for provider, frame in sorted(provider_scores.items()):
        required = {"date", "capital_flow_research_score"}
        if missing := required - set(frame.columns):
            raise ValueError(f"Provider {provider} missing: " + ", ".join(sorted(missing)))
        part = frame[["date", "capital_flow_research_score"]].rename(columns={"capital_flow_research_score": provider})
        merged = part if merged is None else merged.merge(part, on="date", how="inner")
    correlations: list[float] = []
    providers = tuple(sorted(provider_scores))
    assert merged is not None
    for i, a in enumerate(providers):
        for b in providers[i + 1:]:
            corr = _safe_spearman(merged[a], merged[b])
            if corr is not None:
                correlations.append(corr)
    minimum = min(correlations) if correlations else None
    status = "pass" if minimum is not None and minimum >= cfg.minimum_provider_correlation else "fail"
    return ProviderRobustness(providers, tuple(correlations), minimum, status)


def build_outcome_report(frame: pd.DataFrame, *, provider_scores: dict[str, pd.DataFrame] | None = None,
                         config: OutcomeValidationConfig | None = None) -> CapitalFlowOutcomeReport:
    cfg = config or OutcomeValidationConfig()
    required = {"date", "price_usd", "capital_flow_research_score"}
    if missing := required - set(frame.columns):
        raise ValueError("Capital-flow outcome validation missing: " + ", ".join(sorted(missing)))
    labelled = add_future_outcomes(frame, horizons=cfg.horizons)
    horizons = tuple(evaluate_horizon(labelled, h, cfg) for h in cfg.horizons)
    walk = evaluate_walk_forward(labelled, cfg)
    robustness = evaluate_provider_robustness(provider_scores or {}, cfg)
    monotonic_count = sum(x.monotonic_return_bands for x in horizons)
    reasons: list[str] = []
    if monotonic_count < cfg.minimum_monotonic_horizons:
        reasons.append("insufficient monotonic separation across outcome horizons")
    if walk.status != "pass":
        reasons.append("walk-forward stability gate failed")
    if robustness.status != "pass":
        reasons.append("cross-provider robustness gate failed")
    if any(x.status == "insufficient_data" for x in horizons):
        reasons.append("one or more horizons lack sufficient history")
    if not reasons and all(x.status == "pass" for x in horizons):
        overall, decision = "pass", PROMOTE
    elif monotonic_count >= 1 and not any(x.status == "insufficient_data" for x in horizons):
        overall, decision = "mixed", RESEARCH_ONLY
    else:
        overall, decision = "fail", NOT_READY
    payload = labelled[["date", "price_usd", "capital_flow_research_score"]].to_csv(index=False)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return CapitalFlowOutcomeReport(horizons, walk, robustness, overall, decision,
                                    tuple(reasons) or ("all configured promotion gates passed",), False, digest)


def save_outcome_report(report: CapitalFlowOutcomeReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")


def report_frame(report: CapitalFlowOutcomeReport) -> pd.DataFrame:
    return pd.DataFrame([asdict(item) for item in report.horizons])
