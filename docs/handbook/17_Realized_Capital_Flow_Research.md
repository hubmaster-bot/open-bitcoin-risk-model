# Realized Capital Flow Research

OBRM v0.10.3 adds a research-only layer for evidence describing capital entering or leaving Bitcoin. It does not promote Realized Capital Flow into a live Market Dimension.

## Accepted metric families

The importer supports realized-cap growth or change, realized value flow, gross capital inflow, gross capital outflow, net capital flow, exchange netflow and documented custom capital-flow metrics. Custom metrics must state whether positive values represent inflow or outflow.

## Research outputs

The normalized daily series produces an expanding percentile, 30-day smoothing, 90-day absolute change, trailing-year percentile, trend direction, acceleration and a bounded Capital Flow Research Score. Higher scores mean stronger net capital inflow after applying the metric's declared direction.

## Evidence controls

Every import requires provider, provider metric, definition and licence information. The canonical Parquet file is paired with provenance metadata and a SHA-256 digest. Loading fails when integrity verification does not match.

## Limitations


The score is diagnostic, provider definitions may differ, and exchange netflow is only a proxy for sell-side pressure. Multi-provider equivalence and outcome validation are planned for v0.10.4.
=======
The score is diagnostic, provider definitions may differ, and exchange netflow is only a proxy for sell-side pressure. Multi-provider equivalence was completed in v0.10.4 and outcome validation in v0.10.5.

