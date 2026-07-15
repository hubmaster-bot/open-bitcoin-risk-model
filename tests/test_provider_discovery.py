"""Tests for fallback-provider discovery."""

import pytest

from obrm.evidence.provider_discovery import (
    DISCOVERY_STATUS_REVIEW,
    DISCOVERY_STATUS_SUITABLE,
    DISCOVERY_STATUS_UNSUITABLE,
    PROVIDER_CANDIDATES,
    assess_provider_candidate,
    candidates_for_evidence,
    provider_candidate_by_key,
)


def test_candidate_keys_are_unique() -> None:
    keys = [candidate.key for candidate in PROVIDER_CANDIDATES]
    assert len(keys) == len(set(keys))


def test_missing_evidence_has_multiple_fallback_candidates() -> None:
    assert len(candidates_for_evidence("holder_behaviour")) >= 2
    assert len(candidates_for_evidence("realized_capital_flow")) >= 2


def test_candidates_are_sorted_by_priority() -> None:
    candidates = candidates_for_evidence("holder_behaviour")
    priorities = [candidate.priority for candidate in candidates]
    assert priorities == sorted(priorities)


def test_full_assessment_is_suitable() -> None:
    result = assess_provider_candidate(
        provider_key="bitcoin_visuals",
        evidence_key="holder_behaviour",
        access_confirmed=True,
        free_access_confirmed=True,
        historical_coverage_confirmed=True,
        metric_definition_confirmed=True,
        reproducibility_confirmed=True,
        licensing_confirmed=True,
    )
    assert result.status == DISCOVERY_STATUS_SUITABLE
    assert result.score == pytest.approx(1.0)
    assert not result.blockers


def test_partial_assessment_remains_under_review() -> None:
    result = assess_provider_candidate(
        provider_key="bitcoin_visuals",
        evidence_key="holder_behaviour",
        access_confirmed=True,
        free_access_confirmed=True,
        historical_coverage_confirmed=True,
        metric_definition_confirmed=False,
        reproducibility_confirmed=False,
        licensing_confirmed=False,
    )
    assert result.status == DISCOVERY_STATUS_REVIEW
    assert result.score == pytest.approx(0.5)


def test_low_assessment_is_unsuitable() -> None:
    result = assess_provider_candidate(
        provider_key="bitcoin_visuals",
        evidence_key="holder_behaviour",
        access_confirmed=True,
        free_access_confirmed=False,
        historical_coverage_confirmed=False,
        metric_definition_confirmed=False,
        reproducibility_confirmed=False,
        licensing_confirmed=False,
    )
    assert result.status == DISCOVERY_STATUS_UNSUITABLE


def test_provider_cannot_be_assessed_for_unregistered_evidence() -> None:
    with pytest.raises(ValueError):
        assess_provider_candidate(
            provider_key="mempool_space",
            evidence_key="realized_capital_flow",
            access_confirmed=True,
            free_access_confirmed=True,
            historical_coverage_confirmed=True,
            metric_definition_confirmed=True,
            reproducibility_confirmed=True,
            licensing_confirmed=True,
        )


def test_unknown_candidate_is_rejected() -> None:
    with pytest.raises(KeyError):
        provider_candidate_by_key("unknown")
