# ADR-002: Introduce a Market Data Engine

## Status

Accepted

## Decision

OBRM will access market data through a provider-independent Market Data Engine.

The dashboard and future indicator modules will request standardized datasets from the engine rather than reading Parquet files or calling external APIs directly.

## Rationale

- Providers can be replaced without changing downstream code.
- Cached datasets support reproducibility and offline use.
- Provider fallbacks improve reliability.
- Dataset metadata improves auditability.
- A standard schema reduces coupling between data sources and indicators.

## Standard BTC price schema

- `date`
- `price_usd`
- `provider`
