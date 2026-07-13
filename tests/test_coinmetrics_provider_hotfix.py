"""Regression tests for Coin Metrics catalogue discovery."""

from typing import Any

from obrm.research_data.coinmetrics import CoinMetricsCommunityProvider


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
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, **kwargs: Any) -> FakeResponse:
        self.calls.append({"url": url, "params": kwargs.get("params")})
        return self.responses.pop(0)


def test_catalogue_falls_back_to_unfiltered_request_after_400() -> None:
    session = FakeSession(
        [
            FakeResponse(
                {},
                status_code=400,
                text="unsupported parameter",
            ),
            FakeResponse(
                {
                    "data": [
                        {"asset": "eth", "metrics": ["OtherMetric"]},
                        {"asset": "btc", "metrics": ["CapMVRVCur"]},
                    ]
                }
            ),
        ]
    )
    provider = CoinMetricsCommunityProvider(session=session)
    result = provider.discover_asset_metrics("btc")

    assert [item.metric for item in result] == ["CapMVRVCur"]
    assert session.calls[1]["params"] is None


def test_catalogue_accepts_string_metric_entries() -> None:
    session = FakeSession(
        [
            FakeResponse(
                {
                    "data": [
                        {
                            "asset": "btc",
                            "metrics": ["CapRealUSD", "CapMVRVCur"],
                        }
                    ]
                }
            )
        ]
    )
    provider = CoinMetricsCommunityProvider(session=session)
    result = provider.discover_asset_metrics("btc")

    assert [item.metric for item in result] == [
        "CapMVRVCur",
        "CapRealUSD",
    ]
