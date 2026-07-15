"""Core evidence-registry models."""

from __future__ import annotations

from dataclasses import dataclass


EVIDENCE_STATUS_VALIDATED = "validated"
EVIDENCE_STATUS_RESEARCH = "research"
EVIDENCE_STATUS_MISSING = "missing"
EVIDENCE_STATUS_PLANNED = "planned"

VALID_EVIDENCE_STATUSES: frozenset[str] = frozenset(
    {
        EVIDENCE_STATUS_VALIDATED,
        EVIDENCE_STATUS_RESEARCH,
        EVIDENCE_STATUS_MISSING,
        EVIDENCE_STATUS_PLANNED,
    }
)

PROVIDER_STATUS_VALIDATED = "validated"
PROVIDER_STATUS_AVAILABLE = "available"
PROVIDER_STATUS_FORBIDDEN = "forbidden"
PROVIDER_STATUS_CANDIDATE = "candidate"
PROVIDER_STATUS_FUTURE = "future"

VALID_PROVIDER_STATUSES: frozenset[str] = frozenset(
    {
        PROVIDER_STATUS_VALIDATED,
        PROVIDER_STATUS_AVAILABLE,
        PROVIDER_STATUS_FORBIDDEN,
        PROVIDER_STATUS_CANDIDATE,
        PROVIDER_STATUS_FUTURE,
    }
)


@dataclass(frozen=True)
class EvidenceItem:
    """A logical piece of market evidence independent of any provider."""

    key: str
    display_name: str
    domain: str
    intended_dimension: str
    purpose: str
    status: str
    required_for_dimension: bool
    documentation: str
    target_version: str | None = None


@dataclass(frozen=True)
class EvidenceProviderMapping:
    """A provider-specific way to satisfy one logical evidence item."""

    evidence_key: str
    provider: str
    provider_metric: str | None
    status: str
    definition: str
    provenance_note: str
    priority: int = 100
