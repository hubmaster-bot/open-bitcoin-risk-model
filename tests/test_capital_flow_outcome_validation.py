import numpy as np
import pandas as pd

from obrm.research.capital_flow_validation import (
    NOT_READY, PROMOTE, RESEARCH_ONLY, OutcomeValidationConfig,
    add_future_outcomes, build_outcome_report, evaluate_provider_robustness,
)


def synthetic(rows=1800, seed=7):
    rng = np.random.default_rng(seed)
    score = np.clip(rng.beta(2, 2, rows), 0, 1)
    daily = 0.0002 + (score - 0.5) * 0.003 + rng.normal(0, 0.002, rows)
    price = 10000 * np.exp(np.cumsum(daily))
    return pd.DataFrame({"date": pd.date_range("2018-01-01", periods=rows),
                         "price_usd": price, "capital_flow_research_score": score})


def test_future_outcomes_are_forward_labels():
    out = add_future_outcomes(synthetic(500), horizons=(30,))
    assert "forward_return_30d" in out
    assert "forward_max_drawdown_30d" in out
    assert out["forward_return_30d"].tail(30).isna().all()


def test_provider_robustness_passes_correlated_scores():
    frame = synthetic(500)
    providers = {"coin_metrics": frame, "glassnode": frame.assign(capital_flow_research_score=lambda x: x.capital_flow_research_score * .99 + .005)}
    result = evaluate_provider_robustness(providers, OutcomeValidationConfig(minimum_provider_count=2))
    assert result.status == "pass"
    assert result.minimum_correlation > .99


def test_report_preserves_live_model():
    frame = synthetic()
    providers = {p: frame.copy() for p in ("coin_metrics", "glassnode", "cryptoquant")}
    cfg = OutcomeValidationConfig(minimum_rows=300, minimum_band_rows=20, minimum_monotonic_horizons=1)
    report = build_outcome_report(frame, provider_scores=providers, config=cfg)
    assert report.promotion_decision in {PROMOTE, RESEARCH_ONLY, NOT_READY}
    assert report.live_model_changed is False
    assert len(report.generated_from_hash) == 64
    assert len(report.horizons) == 4


def test_missing_provider_validation_blocks_promotion():
    frame = synthetic()
    cfg = OutcomeValidationConfig(minimum_rows=300, minimum_band_rows=20, minimum_monotonic_horizons=1)
    report = build_outcome_report(frame, provider_scores={}, config=cfg)
    assert report.promotion_decision != PROMOTE
    assert "cross-provider robustness gate failed" in report.rationale
