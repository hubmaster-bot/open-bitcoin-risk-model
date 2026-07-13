# ADR-019: Discover capabilities before selecting on-chain metrics

## Status

Accepted

## Decision

OBRM will not hard-code assumed on-chain metric identifiers in v0.9.0.

It will first:

1. query the Coin Metrics Community BTC metric catalogue,
2. save local capability metadata,
3. review frequency and historical coverage,
4. then select metrics in v0.9.1.

## Rationale

Provider availability, naming, coverage, and licensing can change. Capability-first selection prevents the analytics layer from being built around unavailable or inadequately covered metrics.
