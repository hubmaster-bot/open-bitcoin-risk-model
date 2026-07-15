# ADR-032: Require declared equivalence for multi-provider capital-flow validation

## Status
Accepted in v0.10.4.

## Decision
OBRM supports validation inputs from Coin Metrics, Glassnode, CryptoQuant, and CoinGecko through provider-neutral canonical frames. A provider series may be compared only after its metric, unit, sign direction, and transformation are explicitly mapped to the same canonical definition.

CoinGecko market-cap history is retained as a possible proxy dataset, not treated as realized capitalization. Similar labels and high correlation are insufficient to establish semantic equivalence.

Validation reports measure overlap, coverage, Pearson and Spearman correlation, normalized mean absolute error, and directional disagreement. Reports are research artifacts and cannot change Composite Risk.

## Consequences
Provider access tiers and API identifiers remain configurable. Live credentials are never committed. Failed and inconclusive comparisons remain visible.
