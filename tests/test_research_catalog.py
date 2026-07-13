"""Tests for research metric capability filtering."""

from obrm.research_data.catalog import filter_capabilities
from obrm.research_data.models import MetricCapability


def _capabilities() -> tuple[MetricCapability, ...]:
    return (
        MetricCapability(
            provider="Test",
            asset="btc",
            metric="RealizedMetric",
            frequencies=("1d",),
            min_time="2011-01-01",
            max_time="2026-01-01",
            community_available=True,
            description="Realized value metric",
        ),
        MetricCapability(
            provider="Test",
            asset="btc",
            metric="HourlyMetric",
            frequencies=("1h",),
            min_time=None,
            max_time=None,
            community_available=True,
            description="Hourly activity",
        ),
    )


def test_filter_by_daily_frequency() -> None:
    result = filter_capabilities(_capabilities(), frequency="1d")
    assert [item.metric for item in result] == ["RealizedMetric"]


def test_filter_by_search_text() -> None:
    result = filter_capabilities(
        _capabilities(),
        frequency=None,
        search="realized",
    )
    assert [item.metric for item in result] == ["RealizedMetric"]
