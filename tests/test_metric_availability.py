"""Tests for empirical provider metric validation."""

from typing import Any

import requests

from obrm.research_data.availability import (
    STATUS_AVAILABLE,
    STATUS_FORBIDDEN,
    STATUS_SKIPPED,
    probe_metric,
)
from obrm.research_data.coinmetrics import CoinMetricsCommunityProvider
from obrm.research_data.models import MetricCapability


class FakeResponse:
    def __init__(
        self,
        payload: dict[str, Any],
        *,
        status_code: int = 200,
        text: str = "",
        reason: str = "OK",
    ) -> None:
        self.payload = payload
        self.status_code = status_code
        self.text = text
        self.reason = reason

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.headers: dict[str, str] = {}

    def get(self, *args: Any, **kwargs: Any) -> FakeResponse:
        return self.responses.pop(0)


def _capability(
    metric: str = "MetricA",
    frequencies: tuple[str, ...] = ("1d",),
) -> MetricCapability:
    return MetricCapability(
        provider="Test",
        asset="btc",
        metric=metric,
        frequencies=frequencies,
        min_time=None,
        max_time=None,
        community_available=True,
    )


def test_probe_marks_successful_metric_available() -> None:
    session = FakeSession(
        [
            FakeResponse(
                {
                    "data": [
                        {
                            "asset": "btc",
                            "time": "2025-01-01T00:00:00Z",
                            "MetricA": "1.5",
                        }
                    ]
                }
            )
        ]
    )

    result = probe_metric(
        CoinMetricsCommunityProvider(session=session),
        _capability(),
    )

    assert result.status == STATUS_AVAILABLE
    assert result.observations == 1


def test_probe_marks_403_metric_forbidden() -> None:
    session = FakeSession(
        [
            FakeResponse(
                {"error": {"message": "forbidden"}},
                status_code=403,
                text="forbidden",
                reason="Forbidden",
            )
        ]
    )

    result = probe_metric(
        CoinMetricsCommunityProvider(session=session),
        _capability(),
    )

    assert result.status == STATUS_FORBIDDEN
    assert "HTTP 403" in result.detail


def test_probe_skips_non_daily_metric() -> None:
    result = probe_metric(
        CoinMetricsCommunityProvider(
            session=FakeSession([])
        ),
        _capability(frequencies=("1h",)),
    )

    assert result.status == STATUS_SKIPPED
