"""Tests for capability-aware on-chain metric resolution."""

from obrm.onchain.registry import resolve_metric_specs
from obrm.research_data.models import MetricCapability


def test_required_metrics_resolve_from_catalogue() -> None:
    capabilities = (
        MetricCapability("Test", "btc", "CapRealUSD", ("1d",), None, None, True),
        MetricCapability("Test", "btc", "CapMVRVCur", ("1d",), None, None, True),
    )
    resolution = resolve_metric_specs(capabilities)
    assert not resolution.unresolved_required
    assert {item.key for item in resolution.resolved} >= {
        "realized_cap_usd",
        "mvrv",
    }


def test_missing_optional_metric_does_not_block_resolution() -> None:
    capabilities = (
        MetricCapability("Test", "btc", "CapRealUSD", ("1d",), None, None, True),
        MetricCapability("Test", "btc", "CapMVRVCur", ("1d",), None, None, True),
    )
    resolution = resolve_metric_specs(capabilities)
    assert resolution.unresolved_optional == ("Supply Active in One Year",)
