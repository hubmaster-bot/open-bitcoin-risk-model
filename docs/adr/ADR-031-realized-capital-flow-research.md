# ADR-031: Provider-Neutral Realized Capital Flow Research

**Status:** Accepted  
**Version:** 0.10.3

## Decision

Introduce `obrm/research/capital_flow/` as a provider-neutral research boundary for reviewed daily capital-flow evidence. The module records definition, licence, source and metric-direction semantics, persists canonical Parquet with SHA-256 metadata, and produces no-look-ahead diagnostic features.

Supported families are realized-cap growth/change, realized value flow, capital inflow/outflow, net capital flow, exchange netflow and documented custom metrics. Higher research score means stronger net capital inflow. The score remains isolated from Composite Risk and live decisions.

## Consequences

Provider definitions are not treated as interchangeable. Validation hooks and a stable validation view are exposed for later forward-return and multi-provider testing. v0.10.4 will address cross-provider validation rather than silently combining sources.
