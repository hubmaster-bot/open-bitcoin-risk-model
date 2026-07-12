# Multi-Factor Risk Engine

## Components

### Valuation risk — 45%

Price position relative to expanding log-regression fair value.

### Momentum risk — 30%

Combines:

- 30-day return percentile
- 90-day return percentile
- distance from the 200-day moving average

### Volatility risk — 25%

Combines:

- 30-day annualised realised volatility percentile
- drawdown from the all-time high

## Confidence v1

Confidence v1 combines:

- regression quality and sample maturity
- component agreement
- component coverage
- data quality

It is not a forecast probability.

## Decision Engine preview

The Decision Engine can return:

- aggressive accumulation
- accumulation
- normal DCA
- reduced DCA
- pause new DCA
- gradual DCA out
- stronger DCA out

DCA-out guidance is not validated until backtesting is added.
