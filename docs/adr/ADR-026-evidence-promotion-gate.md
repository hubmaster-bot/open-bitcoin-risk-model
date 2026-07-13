# ADR-026: Require validation before Market Dimension promotion

## Status

Accepted

## Decision

A research signal cannot enter Composite Risk until it passes a visible
promotion gate covering:

- evidence-category coverage,
- forward-return separation,
- independence from existing dimensions,
- historical stability.

## Current provisional thresholds

- at least 75% intended evidence-category coverage,
- at least 75% adjacent score-band ordering,
- absolute correlation no greater than 0.80 with existing dimensions,
- usable historical coverage of at least 80%.

## Consequence

The v0.9.3 On-Chain Research Score remains outside Composite Risk unless the
v0.9.4 Validation Lab reports it ready and the result survives review.
