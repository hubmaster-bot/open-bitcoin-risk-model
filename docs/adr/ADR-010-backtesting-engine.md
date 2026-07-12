# ADR-010: Contribution-matched historical backtesting

## Status
Accepted

## Decision
OBRM compares fixed DCA and dynamic OBRM allocation using identical weekly external cash contributions. Dynamic allocation may retain cash, deploy accumulated cash, pause buying, or sell a percentage of BTC holdings. Sale proceeds remain as cash.

## Rationale
Comparing strategies with different external contributions is misleading. Contribution matching makes wealth and drawdown comparisons more meaningful.

## Limitations
Version 0.6.0 excludes fees, bid/ask spread, slippage, taxes, custody risk, exchange failures, execution delay, and behavioural deviations. Results are exploratory, not proof of future outperformance.
