# ADR-003: Use Coin Metrics Community as the primary historical source

## Status

Accepted

## Decision

OBRM will use the Coin Metrics community BTC archive as its primary free historical price source, with Yahoo Finance and Bitstamp retained as fallbacks.

## Rationale

- The archive is updated daily.
- It provides a stable per-asset CSV structure.
- It includes `PriceUSD` and additional public metrics useful for future indicators.
- It supports reproducible research better than relying on a single exchange.
- It is free for community use under CC BY-NC 4.0.

## Consequence

OBRM must retain attribution and remain mindful that the community archive is non-commercially licensed.
