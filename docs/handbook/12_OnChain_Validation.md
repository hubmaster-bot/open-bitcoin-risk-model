# Research Handbook — On-Chain Validation

## Question

Does the provisional on-chain evidence improve OBRM beyond price-derived
Valuation, Momentum, and Volatility?

## Forward returns

OBRM evaluates later BTC returns over 30, 90, 180, 365, and 730 days.

The model score is calculated first. Future returns are attached afterward only
as outcome labels.

## Bucket analysis

Historical scores are grouped into five bands from 0.0–0.2 through 0.8–1.0.

Useful risk evidence should generally show weaker future returns as the score
rises.

## Redundancy

Pearson correlation is measured against:

- Valuation
- Momentum
- Volatility
- Composite Risk v1

A highly correlated candidate may add little independent information.

## Incremental model experiment

Research Composite v2 is:

`80% Composite Risk v1 + 20% provisional On-Chain Research Score`

This score is validation-only and cannot influence live decisions.

## Promotion gate

Coverage, separation, independence, and stability must all pass before a
separate release may promote On-Chain into Composite Risk.
