# ADR-009: Introduce a transparent multi-factor risk engine

## Status

Accepted

## Decision

OBRM v0.5.0 combines three components:

- Valuation risk: 45%
- Momentum risk: 30%
- Volatility risk: 25%

The first Confidence Engine combines model quality, component agreement, component coverage, and data quality.

## Rationale

A single valuation model can remain elevated or depressed for extended periods. Adding momentum and volatility provides a broader description of market conditions while preserving transparency.

## Limitations

- Weights are provisional and require backtesting.
- No on-chain or macro components are included.
- DCA-out guidance is preview-only.
- Confidence is model confidence, not return probability.
