# ADR-024: Validate provider availability empirically

## Status

Accepted

## Context

Coin Metrics catalogue discovery confirmed that a metric exists, but live
Community API downloads returned HTTP 403 for some metrics such as
`CapRealUSD`.

## Decision

OBRM v0.9.2 introduces a Community Metric Validator.

For each candidate metric, OBRM performs a small real time-series request and
records one of:

- available
- forbidden
- empty
- error
- skipped

Only empirically available metrics may be selected by the on-chain analytics
service.

## Rationale

Catalogue presence, licensing metadata, and actual Community access are
different concepts. The verified local registry is the reliable boundary.

## Multi-provider future

A metric rejected by Coin Metrics is not rejected by OBRM. Future provider
adapters may supply the same logical metric with explicit provenance and
definition metadata.
