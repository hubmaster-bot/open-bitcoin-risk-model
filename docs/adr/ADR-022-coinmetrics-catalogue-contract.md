# ADR-022: Follow the documented asset-metric catalogue contract

## Status

Accepted

## Context

The Coin Metrics Community `catalog/asset-metrics` endpoint rejected both
`limit` and filtered variants during live testing.

## Decision

OBRM v0.9.1.2 requests the catalogue endpoint without query parameters and
filters the returned catalogue locally to Bitcoin.

The provider continues to follow `next_page_url` when one is supplied.

## Rationale

The official Coin Metrics API reference shows the asset-metric catalogue
request without `assets`, `limit`, or pagination-size query parameters.
Provider adapters must follow the documented endpoint contract rather than
infer parameters from other catalogue endpoints.

## Testing

The maintenance release replaces both legacy provider test modules with
complete, realistic response doubles.
