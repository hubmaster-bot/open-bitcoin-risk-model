import numpy as np
import pandas as pd
import pytest

from obrm.research.provider_validation import (
    PROVIDER_CANDIDATES, ProviderMetricMapping, ValidationThresholds,
    build_multi_provider_report, canonicalize_provider_series, compare_provider_pair,
)


def raw(seed=0, scale=1.0, noise=0.0, rows=500):
    rng=np.random.default_rng(seed)
    base=np.cumsum(rng.normal(10, 2, rows))*scale + 1_000_000
    values=base + rng.normal(0, noise, rows)
    return pd.DataFrame({"date":pd.date_range("2020-01-01", periods=rows), "value":values})


def mapping(provider):
    return ProviderMetricMapping(provider, "metric", "realized_cap_usd", "USD", "inflow", "diff")


def test_catalog_has_requested_providers():
    assert set(PROVIDER_CANDIDATES)=={"coin_metrics","glassnode","cryptoquant","coingecko"}
    assert PROVIDER_CANDIDATES["coingecko"].canonical_metric == "market_cap_proxy_usd"


def test_canonicalization_applies_diff_and_direction():
    frame=canonicalize_provider_series(raw(rows=10), mapping("coin_metrics"))
    assert len(frame)==9
    assert {"canonical_value","provider","canonical_metric"} <= set(frame.columns)


def test_equivalent_provider_pair_passes():
    a=canonicalize_provider_series(raw(seed=2), mapping("coin_metrics"))
    b=canonicalize_provider_series(raw(seed=2, noise=.01), mapping("glassnode"))
    result=compare_provider_pair(a,b)
    assert result.status=="pass"
    assert result.overlap_days==499


def test_divergent_pair_fails():
    a=canonicalize_provider_series(raw(seed=2), mapping("coin_metrics"))
    b=canonicalize_provider_series(raw(seed=9), mapping("cryptoquant"))
    result=compare_provider_pair(a,b)
    assert result.status=="fail"
    assert result.reasons


def test_report_requires_same_metric_and_two_providers():
    a=canonicalize_provider_series(raw(seed=2), mapping("coin_metrics"))
    with pytest.raises(ValueError): build_multi_provider_report({"a":a})
    other=ProviderMetricMapping("coingecko","m","market_cap_proxy_usd","USD","inflow","diff")
    b=canonicalize_provider_series(raw(seed=2),other)
    with pytest.raises(ValueError): build_multi_provider_report({"a":a,"b":b})


def test_report_builds_all_pairs():
    frames={p:canonicalize_provider_series(raw(seed=4, noise=i*.01), mapping(p))
            for i,p in enumerate(("coin_metrics","glassnode","cryptoquant"))}
    report=build_multi_provider_report(frames, ValidationThresholds(minimum_overlap_days=300))
    assert report.overall_status=="pass"
    assert len(report.pairwise)==3
    assert len(report.generated_from_hash)==64
