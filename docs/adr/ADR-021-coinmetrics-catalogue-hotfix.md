# ADR-021: Bound and paginate Coin Metrics catalogue requests

## Status

Accepted

## Context

OBRM requested the Coin Metrics asset-metric catalogue with `limit=10000`.
The Community endpoint rejected that request with HTTP 400.

## Decision

OBRM v0.9.1.1:

- uses a bounded catalogue limit of 1000,
- follows `next_page_url` until all pages are read,
- retries the catalogue without the asset filter when a filtered request returns HTTP 400,
- filters the fallback response locally,
- includes the provider response body in raised errors,
- preserves any existing local catalogue when refresh fails.

## Rationale

The official API documentation shows bounded catalogue requests and supports pagination. OBRM should not assume that a complete catalogue can be retrieved in one oversized request.

## Scope

This hotfix changes the provider integration only. It does not alter on-chain analytics or model outputs.
