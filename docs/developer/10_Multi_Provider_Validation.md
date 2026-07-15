# Multi-Provider Validation

The `obrm.research.provider_validation` package provides the v0.10.4 validation layer.

1. Create or select a `ProviderMetricMapping`.
2. Normalize a reviewed export with `canonicalize_provider_series()`.
3. Compare two canonical frames with `compare_provider_pair()`, or build every pair with `build_multi_provider_report()`.
4. Persist the immutable JSON report with `save_report()`.

Supported provider identifiers are `coin_metrics`, `glassnode`, `cryptoquant`, and `coingecko`. The bundled catalogue documents candidate metrics but does not claim current entitlement or live endpoint availability. API credentials belong in environment variables in downstream adapters.

A report passes only when every pair passes the configured overlap, coverage, correlation, error, and direction thresholds. Passing establishes empirical agreement for the tested period; it does not by itself prove identical methodology or authorize promotion into Composite Risk.
