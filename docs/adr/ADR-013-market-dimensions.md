# ADR-013: Describe model inputs as Market Dimensions

## Status

Accepted

## Decision

OBRM will use the term **Market Dimensions** for valuation, momentum, volatility, and future analytical dimensions.

## Rationale

The inputs do not all measure the same kind of risk:

- Valuation describes price relative to fair value.
- Momentum describes price direction and strength.
- Volatility describes stability and turbulence.

Calling them Market Dimensions is more precise and prepares the architecture for on-chain, macro, and market-structure dimensions.

## Standard score vocabulary

- 0.00–0.20: Deep Value
- 0.20–0.40: Attractive
- 0.40–0.60: Neutral
- 0.60–0.75: Elevated
- 0.75–0.90: High
- 0.90–1.00: Extreme
