# User Guide — Validation and Backtesting

## Backtesting Lab

Compares:

- Fixed DCA
- OBRM Dynamic

Both strategies receive identical external contributions.

The dynamic strategy may:

- buy more aggressively,
- retain cash,
- pause buying,
- or gradually sell BTC.

## Validation Lab

Tests whether lower historical risk bands generally preceded better future-return environments.

Current horizons:

- 90 days
- 365 days
- 730 days

## No-look-ahead rule

The historical risk score is calculated first using only information available at the time.

Future returns are calculated afterward only as outcome labels.

## Limitations

Historical evidence is not proof of future performance.
