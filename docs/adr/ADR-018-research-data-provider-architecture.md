# ADR-018: Generalise external research-data providers

## Status

Accepted

## Decision

OBRM v0.9.0 introduces a provider-independent research-data contract for on-chain, macro, and market-structure sources.

The first implementation is the Coin Metrics Community API v4 adapter.

## Architecture

External Provider → Provider Adapter → Schema Normalisation →
Validation and Provenance → Canonical Local Dataset → Analytics

## Rationale

The analytics layer must not depend directly on one vendor's endpoint structure, field naming, or authentication model.

This allows OBRM to replace or supplement providers without rewriting the model.

## Coin Metrics Community

The Community API is keyless and exposes catalogue and time-series endpoints. OBRM locally stores discovered capabilities before selecting metrics.

## v2.0 direction

Self-built metrics from Bitcoin Core remain a long-term maximum-transparency research path.
