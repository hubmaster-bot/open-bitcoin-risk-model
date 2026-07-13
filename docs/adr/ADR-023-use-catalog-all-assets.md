# ADR-023: Discover metrics from catalog-all/assets

## Status

Accepted

## Context

Live testing showed that `catalog/asset-metrics` did not return the asset-grouped
records expected by OBRM. The request succeeded, but local filtering found no
Bitcoin entries.

## Decision

OBRM v0.9.1.3 uses `catalog-all/assets`, which is the Coin Metrics catalogue
endpoint intended to list supported metrics per asset.

The provider first requests `assets=btc`. If the Community deployment rejects
that filter with HTTP 400, OBRM retries without parameters and filters locally.

## Compatibility

The parser accepts metric entries represented as either strings or objects.
