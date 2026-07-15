"""Tests for provider-discovery persistence."""

from pathlib import Path

from obrm.evidence.discovery_store import (
    load_discovery_registry,
    save_provider_assessment,
)
from obrm.evidence.provider_discovery import assess_provider_candidate


def _assessment(*, access: bool):
    return assess_provider_candidate(
        provider_key="bitcoin_visuals",
        evidence_key="holder_behaviour",
        access_confirmed=access,
        free_access_confirmed=access,
        historical_coverage_confirmed=False,
        metric_definition_confirmed=False,
        reproducibility_confirmed=False,
        licensing_confirmed=False,
    )


def test_store_replaces_existing_provider_evidence_pair(
    tmp_path: Path,
) -> None:
    path = tmp_path / "discovery.json"
    save_provider_assessment(_assessment(access=False), path)
    save_provider_assessment(_assessment(access=True), path)

    payload = load_discovery_registry(path)
    assert payload is not None
    assessments = payload["assessments"]
    assert len(assessments) == 1
    assert assessments[0]["access_confirmed"] is True
