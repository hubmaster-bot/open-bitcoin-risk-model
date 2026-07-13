# ADR-020: Begin on-chain analytics with capability-resolved metrics

## Status

Accepted

## Decision

OBRM v0.9.1 begins with:

- Realized Capitalization
- MVRV
- optional one-year active supply

Provider metric identifiers are resolved from the saved Coin Metrics catalogue rather than assumed blindly.

## Derived analytics

- 365-day realized-cap growth
- expanding MVRV percentile
- expanding realized-cap-growth percentile
- optional active-supply percentile
- smoothed diagnostic research score

## Boundary

The diagnostic score does not yet enter Composite Risk, Model Confidence, decisions, backtests, or Portfolio Lab.
