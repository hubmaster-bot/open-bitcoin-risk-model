"""Provider-independent registry of missing research evidence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderGap:
    logical_metric: str
    evidence_category: str
    current_provider: str
    current_status: str
    preferred_fallback: str
    notes: str


ONCHAIN_PROVIDER_GAPS: tuple[ProviderGap, ...] = (
    ProviderGap(
        logical_metric="Holder Behaviour",
        evidence_category="Holder Behaviour",
        current_provider="Coin Metrics Community",
        current_status="No validated free input",
        preferred_fallback="Additional free provider or Bitcoin Core",
        notes=(
            "Seek dormancy, spent-output, coin-age, or long-term-holder evidence."
        ),
    ),
    ProviderGap(
        logical_metric="Realized Capital Flow",
        evidence_category="Realized Capital Flow",
        current_provider="Coin Metrics Community",
        current_status="Relevant metrics forbidden",
        preferred_fallback="Additional free provider or Bitcoin Core",
        notes=(
            "Seek realized-cap growth or equivalent capital-inflow evidence."
        ),
    ),
)
