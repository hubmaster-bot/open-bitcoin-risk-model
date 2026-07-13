# ADR-025: Keep validated on-chain evidence diagnostic

## Status

Accepted

## Decision

OBRM v0.9.3 builds a validated on-chain research layer using only:

- `CapMVRVCur`
- `HashRate`

These support two evidence categories:

- Realized Valuation
- Network Strength

The following intended categories remain unavailable:

- Holder Behaviour
- Realized Capital Flow

## Consequence

The On-Chain Research Score remains diagnostic and does not enter Composite
Risk, Model Confidence, decisions, Portfolio Lab, or production backtests.

## Rationale

Promoting a partially observed dimension would imply more completeness than the
available evidence supports.
