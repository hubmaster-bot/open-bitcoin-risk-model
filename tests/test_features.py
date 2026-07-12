"""Tests for the OBRM feature registry."""

from obrm.core.features import available_features, planned_features


def test_feature_registry_has_available_and_planned_features() -> None:
    assert available_features()
    assert planned_features()


def test_market_data_fusion_is_available() -> None:
    keys = {feature.key for feature in available_features()}
    assert "market_data_fusion" in keys
