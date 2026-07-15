"""Application service for provider discovery."""

from __future__ import annotations

from obrm.evidence.discovery_paths import PROVIDER_DISCOVERY_FILE
from obrm.evidence.discovery_store import (
    load_discovery_registry,
    save_provider_assessment,
)
from obrm.evidence.provider_discovery import (
    ProviderAssessment,
    ProviderCandidate,
    assess_provider_candidate,
    candidates_for_evidence,
)


def list_candidates_for_evidence(
    evidence_key: str,
) -> tuple[ProviderCandidate, ...]:
    return candidates_for_evidence(evidence_key)


def record_provider_assessment(
    **kwargs: object,
) -> ProviderAssessment:
    assessment = assess_provider_candidate(**kwargs)  # type: ignore[arg-type]
    save_provider_assessment(assessment, PROVIDER_DISCOVERY_FILE)
    return assessment


def load_saved_assessments() -> tuple[dict[str, object], ...]:
    payload = load_discovery_registry(PROVIDER_DISCOVERY_FILE)
    if payload is None:
        return ()
    return tuple(payload.get("assessments", []))
