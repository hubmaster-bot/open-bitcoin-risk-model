"""Provider discovery and transparent candidate assessment.

This module records provider candidates without treating them as validated data
sources. A candidate must pass access, licensing, coverage, definition, and
reproducibility review before it can become an active provider mapping.
"""

from __future__ import annotations

from dataclasses import dataclass


DISCOVERY_STATUS_UNREVIEWED = "unreviewed"
DISCOVERY_STATUS_REVIEW = "under_review"
DISCOVERY_STATUS_SUITABLE = "suitable"
DISCOVERY_STATUS_UNSUITABLE = "unsuitable"
DISCOVERY_STATUS_FUTURE = "future"

VALID_DISCOVERY_STATUSES: frozenset[str] = frozenset(
    {
        DISCOVERY_STATUS_UNREVIEWED,
        DISCOVERY_STATUS_REVIEW,
        DISCOVERY_STATUS_SUITABLE,
        DISCOVERY_STATUS_UNSUITABLE,
        DISCOVERY_STATUS_FUTURE,
    }
)


@dataclass(frozen=True)
class ProviderCandidate:
    """A potential research-data source awaiting formal validation."""

    key: str
    display_name: str
    provider_type: str
    status: str
    evidence_keys: tuple[str, ...]
    access_method: str
    expected_cost: str
    source_url: str | None
    documentation_url: str | None
    notes: str
    priority: int = 100


@dataclass(frozen=True)
class ProviderAssessment:
    """Structured review of one candidate for one logical evidence item."""

    provider_key: str
    evidence_key: str
    access_confirmed: bool
    free_access_confirmed: bool
    historical_coverage_confirmed: bool
    metric_definition_confirmed: bool
    reproducibility_confirmed: bool
    licensing_confirmed: bool
    score: float
    status: str
    blockers: tuple[str, ...]


PROVIDER_CANDIDATES: tuple[ProviderCandidate, ...] = (
    ProviderCandidate(
        key="bitcoin_visuals",
        display_name="Bitcoin Visuals",
        provider_type="Public research website",
        status=DISCOVERY_STATUS_UNREVIEWED,
        evidence_keys=("holder_behaviour", "realized_capital_flow"),
        access_method="Public download, endpoint, or approved manual export",
        expected_cost="Unknown until review",
        source_url="https://bitcoinvisuals.com/",
        documentation_url=None,
        notes=(
            "Candidate only. Confirm machine-readable access, update cadence, "
            "definitions, licensing, and historical coverage before use."
        ),
        priority=20,
    ),
    ProviderCandidate(
        key="blockchain_com_charts",
        display_name="Blockchain.com Charts",
        provider_type="Public chart data",
        status=DISCOVERY_STATUS_UNREVIEWED,
        evidence_keys=("holder_behaviour",),
        access_method="Public chart export or documented endpoint",
        expected_cost="Unknown until review",
        source_url="https://www.blockchain.com/explorer/charts",
        documentation_url=None,
        notes=(
            "Candidate only. Verify that available chart definitions answer "
            "the registered evidence question and permit reproducible use."
        ),
        priority=30,
    ),
    ProviderCandidate(
        key="blockchair",
        display_name="Blockchair",
        provider_type="Blockchain data API",
        status=DISCOVERY_STATUS_UNREVIEWED,
        evidence_keys=("holder_behaviour", "realized_capital_flow"),
        access_method="API or downloadable datasets",
        expected_cost="Unknown until review",
        source_url="https://blockchair.com/",
        documentation_url="https://blockchair.com/api/docs",
        notes=(
            "Candidate only. Confirm free quotas, historical depth, precise "
            "metric definitions, and research redistribution terms."
        ),
        priority=40,
    ),
    ProviderCandidate(
        key="mempool_space",
        display_name="mempool.space",
        provider_type="Open Bitcoin data service",
        status=DISCOVERY_STATUS_UNREVIEWED,
        evidence_keys=("network_strength", "holder_behaviour"),
        access_method="Public API",
        expected_cost="Unknown until review",
        source_url="https://mempool.space/",
        documentation_url="https://mempool.space/docs/api/rest",
        notes=(
            "Candidate only. Network and transaction data may support derived "
            "evidence, but exact fit must be demonstrated."
        ),
        priority=50,
    ),
    ProviderCandidate(
        key="custom_csv",
        display_name="User-Supplied CSV",
        provider_type="Portable research dataset",
        status=DISCOVERY_STATUS_REVIEW,
        evidence_keys=("holder_behaviour", "realized_capital_flow"),
        access_method="Local CSV import",
        expected_cost="Depends on original source",
        source_url=None,
        documentation_url=None,
        notes=(
            "Allows transparent experiments while preserving provider, metric "
            "definition, licence, and dataset-hash metadata."
        ),
        priority=70,
    ),
    ProviderCandidate(
        key="bitcoin_core",
        display_name="Bitcoin Core",
        provider_type="Self-computed node data",
        status=DISCOVERY_STATUS_FUTURE,
        evidence_keys=("holder_behaviour", "realized_capital_flow"),
        access_method="Local node and reproducible calculation pipeline",
        expected_cost="Infrastructure and engineering cost",
        source_url="https://bitcoincore.org/",
        documentation_url="https://bitcoincore.org/en/doc/",
        notes=(
            "Maximum-transparency v2.0 path. Not an immediate v0.10.x provider."
        ),
        priority=100,
    ),
)


def provider_candidate_by_key(key: str) -> ProviderCandidate:
    for candidate in PROVIDER_CANDIDATES:
        if candidate.key == key:
            return candidate
    raise KeyError(f"Unknown provider candidate: {key}")


def candidates_for_evidence(
    evidence_key: str,
) -> tuple[ProviderCandidate, ...]:
    """Return candidates in deterministic research priority order."""
    return tuple(
        sorted(
            (
                candidate
                for candidate in PROVIDER_CANDIDATES
                if evidence_key in candidate.evidence_keys
            ),
            key=lambda candidate: (candidate.priority, candidate.display_name),
        )
    )


def assess_provider_candidate(
    *,
    provider_key: str,
    evidence_key: str,
    access_confirmed: bool,
    free_access_confirmed: bool,
    historical_coverage_confirmed: bool,
    metric_definition_confirmed: bool,
    reproducibility_confirmed: bool,
    licensing_confirmed: bool,
) -> ProviderAssessment:
    """Score a candidate without silently promoting it into production."""
    candidate = provider_candidate_by_key(provider_key)
    if evidence_key not in candidate.evidence_keys:
        raise ValueError(
            f"Provider {provider_key} is not registered for {evidence_key}."
        )

    checks = {
        "Access is not confirmed.": access_confirmed,
        "Free access is not confirmed.": free_access_confirmed,
        "Historical coverage is not confirmed.": historical_coverage_confirmed,
        "Metric definition is not confirmed.": metric_definition_confirmed,
        "Reproducibility is not confirmed.": reproducibility_confirmed,
        "Licensing is not confirmed.": licensing_confirmed,
    }
    blockers = tuple(message for message, passed in checks.items() if not passed)
    score = sum(checks.values()) / len(checks)

    if score == 1.0:
        status = DISCOVERY_STATUS_SUITABLE
    elif score >= 0.5:
        status = DISCOVERY_STATUS_REVIEW
    else:
        status = DISCOVERY_STATUS_UNSUITABLE

    return ProviderAssessment(
        provider_key=provider_key,
        evidence_key=evidence_key,
        access_confirmed=access_confirmed,
        free_access_confirmed=free_access_confirmed,
        historical_coverage_confirmed=historical_coverage_confirmed,
        metric_definition_confirmed=metric_definition_confirmed,
        reproducibility_confirmed=reproducibility_confirmed,
        licensing_confirmed=licensing_confirmed,
        score=score,
        status=status,
        blockers=blockers,
    )
