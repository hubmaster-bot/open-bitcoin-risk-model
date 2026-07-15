# ADR-028: Use an evidence-first research architecture

## Status

Accepted

## Context

The v0.9.x on-chain work showed that provider catalogues, subscription access,
metric definitions, and logical research questions are separate concerns.
Coin Metrics could supply some useful evidence but not every evidence category
required for a complete On-Chain Market Dimension.

## Decision

OBRM v0.10.0 introduces a canonical Evidence Registry. The registry defines the
market question first and records provider mappings separately.

The architecture is:

`Evidence → Provider mapping → Validated dataset → Research signal → Validation → Promotion`

## Consequences

- A provider failure does not invalidate a logical evidence category.
- Multiple providers may satisfy the same evidence item.
- Provider-specific definitions and provenance remain visible.
- Validated evidence must have at least one validated provider mapping.
- Evidence coverage becomes measurable across research domains.
- Future Bitcoin Core calculations can replace or supplement external sources
  without changing downstream evidence identities.

## Initial registry

The initial registry contains eight evidence items. Realized Valuation and
Network Strength are validated. Holder Behaviour and Realized Capital Flow are
missing. Liquidity, Macro, Derivatives, and Sentiment are planned.
