"""Capability-aware Coin Metrics metric selection."""

from __future__ import annotations

from dataclasses import dataclass

from obrm.research_data.models import MetricCapability


@dataclass(frozen=True)
class OnChainMetricSpec:
    key: str
    display_name: str
    aliases: tuple[str, ...]
    required_frequency: str
    purpose: str
    required: bool = True


ONCHAIN_METRIC_SPECS: tuple[OnChainMetricSpec, ...] = (
    OnChainMetricSpec(
        key="realized_cap_usd",
        display_name="Realized Capitalization",
        aliases=("CapRealUSD",),
        required_frequency="1d",
        purpose="Measures the aggregate realized value of Bitcoin supply.",
    ),
    OnChainMetricSpec(
        key="mvrv",
        display_name="MVRV",
        aliases=("CapMVRVCur", "CapMVRVFF"),
        required_frequency="1d",
        purpose="Compares market value with realized value.",
    ),
    OnChainMetricSpec(
        key="active_supply_1y",
        display_name="Supply Active in One Year",
        aliases=("SplyAct1yr", "SplyAct1yrPct"),
        required_frequency="1d",
        purpose="Provides a transparent proxy for holder activity and dormancy.",
        required=False,
    ),
)


@dataclass(frozen=True)
class ResolvedMetric:
    key: str
    display_name: str
    provider_metric: str
    purpose: str
    required: bool


@dataclass(frozen=True)
class MetricResolution:
    resolved: tuple[ResolvedMetric, ...]
    unresolved_required: tuple[str, ...]
    unresolved_optional: tuple[str, ...]


def resolve_metric_specs(
    capabilities: tuple[MetricCapability, ...],
    specs: tuple[OnChainMetricSpec, ...] = ONCHAIN_METRIC_SPECS,
) -> MetricResolution:
    """Resolve logical inputs against the provider catalogue."""
    available = {
        capability.metric: capability
        for capability in capabilities
        if not capability.frequencies or "1d" in capability.frequencies
    }

    resolved: list[ResolvedMetric] = []
    missing_required: list[str] = []
    missing_optional: list[str] = []

    for spec in specs:
        chosen = next(
            (alias for alias in spec.aliases if alias in available),
            None,
        )
        if chosen is None:
            target = missing_required if spec.required else missing_optional
            target.append(spec.display_name)
            continue

        resolved.append(
            ResolvedMetric(
                key=spec.key,
                display_name=spec.display_name,
                provider_metric=chosen,
                purpose=spec.purpose,
                required=spec.required,
            )
        )

    return MetricResolution(
        resolved=tuple(resolved),
        unresolved_required=tuple(missing_required),
        unresolved_optional=tuple(missing_optional),
    )


def provider_metrics(
    resolution: MetricResolution,
) -> tuple[str, ...]:
    return tuple(item.provider_metric for item in resolution.resolved)
