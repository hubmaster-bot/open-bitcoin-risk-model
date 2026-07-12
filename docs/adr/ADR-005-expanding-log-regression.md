# ADR-005: Use expanding log-log regression for first fair-value model

## Status

Accepted

## Decision

OBRM v0.4.0 will estimate Bitcoin fair value using an expanding ordinary least-squares regression:

`log10(price) = intercept + slope × log10(days since Bitcoin genesis)`

Each historical date uses only information available on or before that date.

## Rationale

- Avoids future-data leakage in historical risk values.
- Is transparent and computationally efficient.
- Produces an interpretable fair-value estimate.
- Creates a reusable price-position component for the future composite model.

## Limitations

- Bitcoin may not continue following the same long-term relationship.
- Early-history market structure differs substantially from today.
- v0.4.0 price-position risk is not the full OBRM composite risk score.
- Preliminary confidence measures model fit and sample maturity only.
