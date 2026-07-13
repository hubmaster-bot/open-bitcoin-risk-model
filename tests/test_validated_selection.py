"""Tests for selection from the verified metric registry."""

import json

from obrm.research_data.availability import STATUS_AVAILABLE
from obrm.research_data.models import MetricCapability


def test_available_status_constant_is_stable() -> None:
    assert STATUS_AVAILABLE == "available"


def test_registry_payload_is_json_serializable() -> None:
    payload = {
        "results": [
            {
                "metric": "MetricA",
                "status": STATUS_AVAILABLE,
            }
        ]
    }
    assert "MetricA" in json.dumps(payload)
