"""Tests for the Coin Metrics Community provider adapter."""

from typing import Any

import pandas as pd

from obrm.research_data.coinmetrics import CoinMetricsCommunityProvider


class FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeSession:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self.payloads = payloads
        self.headers: dict[str, str] = {}

    def get(self, *args: Any, **kwargs: Any) -> FakeResponse:
        return FakeResponse(self.payloads.pop(0))


def test_fetch_asset_metrics_standardizes_schema() -> None:
    session = FakeSession(
        [
            {
                "data": [
                    {
                        "asset": "btc",
                        "time": "2026-01-01T00:00:00.000000000Z",
                        "MetricA": "12.5",
                    }
                ]
            }
        ]
    )
    provider = CoinMetricsCommunityProvider(session=session)
    frame = provider.fetch_asset_metrics("btc", ("MetricA",))

    assert list(frame.columns) == [
        "date",
        "MetricA",
        "provider",
        "asset",
    ]
    assert frame.loc[0, "MetricA"] == 12.5
    assert frame.loc[0, "asset"] == "btc"


def test_catalog_discovery_returns_capabilities() -> None:
    session = FakeSession(
        [
            {
                "data": [
                    {
                        "asset": "btc",
                        "metrics": [
                            {
                                "metric": "MetricA",
                                "frequencies": ["1d"],
                                "min_time": "2011-01-01",
                                "max_time": "2026-01-01",
                            }
                        ],
                    }
                ]
            }
        ]
    )
    provider = CoinMetricsCommunityProvider(session=session)
    result = provider.discover_asset_metrics("btc")

    assert len(result) == 1
    assert result[0].metric == "MetricA"
    assert result[0].frequencies == ("1d",)
