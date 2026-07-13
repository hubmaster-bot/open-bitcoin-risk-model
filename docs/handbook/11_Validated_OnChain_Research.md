# Research Handbook — Validated On-Chain Research

## Available evidence

### Realized Valuation

OBRM uses `CapMVRVCur`, the Community-accessible MVRV metric.

MVRV is converted to an expanding percentile using only information available
on or before each date.

### Network Strength

OBRM uses `HashRate`.

Two transparent signals are derived:

- 365-day hash-rate growth
- distance from the 200-day hash-rate trend

Each is converted to an expanding percentile.

## Diagnostic score

The On-Chain Research Score is currently:

`50% Realized Valuation + 50% Network Strength`

A 30-day average reduces daily noise.

## Missing evidence

Holder Behaviour and Realized Capital Flow remain unavailable from the current
validated Community set.

## Decision boundary

The diagnostic score is not yet an official Market Dimension and does not alter
the main model.
