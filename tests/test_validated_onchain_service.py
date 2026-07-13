"""Tests for validated service configuration."""

from obrm.onchain.validated_service import VALIDATED_PROVIDER_METRICS


def test_validated_provider_metrics_are_explicit() -> None:
    assert VALIDATED_PROVIDER_METRICS == (
        "CapMVRVCur",
        "HashRate",
    )
