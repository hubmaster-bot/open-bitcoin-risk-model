"""Validated on-chain evidence registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OnChainEvidenceCategory:
    key: str
    display_name: str
    provider_metric: str | None
    available: bool
    purpose: str
    status_note: str


ONCHAIN_EVIDENCE_CATEGORIES: tuple[OnChainEvidenceCategory, ...] = (
    OnChainEvidenceCategory(
        key="realized_valuation",
        display_name="Realized Valuation",
        provider_metric="CapMVRVCur",
        available=True,
        purpose="Compares market value with realized value.",
        status_note="Validated with Coin Metrics Community access.",
    ),
    OnChainEvidenceCategory(
        key="network_strength",
        display_name="Network Strength",
        provider_metric="HashRate",
        available=True,
        purpose="Measures mining commitment and network security activity.",
        status_note="Validated with Coin Metrics Community access.",
    ),
    OnChainEvidenceCategory(
        key="holder_behaviour",
        display_name="Holder Behaviour",
        provider_metric=None,
        available=False,
        purpose="Would describe dormancy, spending, or long-term holder activity.",
        status_note="No validated free provider input selected yet.",
    ),
    OnChainEvidenceCategory(
        key="capital_flow",
        display_name="Realized Capital Flow",
        provider_metric=None,
        available=False,
        purpose="Would describe changes in realized capitalization or capital inflow.",
        status_note="No validated free provider input selected yet.",
    ),
)


def available_evidence_categories() -> tuple[OnChainEvidenceCategory, ...]:
    return tuple(item for item in ONCHAIN_EVIDENCE_CATEGORIES if item.available)


def intended_evidence_count() -> int:
    return len(ONCHAIN_EVIDENCE_CATEGORIES)


def available_evidence_count() -> int:
    return len(available_evidence_categories())
