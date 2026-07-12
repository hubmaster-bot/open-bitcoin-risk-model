# OBRM Risk Engine

## v0.4.0 scope

Version 0.4.0 introduces the first analytics component:

- Expanding log-regression fair value
- Premium or discount to fair value
- Standardized trend residual
- Price Position Risk from 0 to 1
- Preliminary model confidence
- Descriptive market phase
- Dynamic DCA lookup

## Important distinction

`Price Position Risk` is one future component of OBRM Risk. It is not yet the final composite risk score.

Future releases will add:

- Momentum risk
- Volatility risk
- Market-structure risk
- On-chain risk
- Macro risk
- Full confidence engine

## Confidence in v0.4.0

Preliminary confidence combines:

- expanding regression fit, and
- sample maturity.

It does not represent the probability of a positive return.
