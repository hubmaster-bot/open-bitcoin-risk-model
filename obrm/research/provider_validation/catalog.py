"""Declared provider candidates for v0.10.4.

Metric identifiers are configurable because access tiers and provider catalogues
change. These declarations document intended roles; they do not claim live API
availability or semantic equivalence.
"""
from .core import ProviderMetricMapping

PROVIDER_CANDIDATES = {
    "coin_metrics": ProviderMetricMapping(
        provider="coin_metrics", provider_metric="CapRealUSD", canonical_metric="realized_cap_usd",
        unit="USD", positive_direction="inflow", transformation="diff",
        definition="Daily change in realized capitalization.", access_tier="provider-dependent"),
    "glassnode": ProviderMetricMapping(
        provider="glassnode", provider_metric="market/marketcap_realized_usd", canonical_metric="realized_cap_usd",
        unit="USD", positive_direction="inflow", transformation="diff",
        definition="Daily change in realized capitalization.", access_tier="provider-dependent"),
    "cryptoquant": ProviderMetricMapping(
        provider="cryptoquant", provider_metric="realized-cap", canonical_metric="realized_cap_usd",
        unit="USD", positive_direction="inflow", transformation="diff",
        definition="Daily change in realized capitalization.", access_tier="provider-dependent"),
    "coingecko": ProviderMetricMapping(
        provider="coingecko", provider_metric="market_chart.market_caps", canonical_metric="market_cap_proxy_usd",
        unit="USD", positive_direction="inflow", transformation="diff",
        definition="Market-cap change proxy; not realized capitalization and therefore not equivalent by default.",
        access_tier="public-or-keyed"),
}
