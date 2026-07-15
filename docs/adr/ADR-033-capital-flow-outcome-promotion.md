# ADR-033: Require outcome validation before capital-flow promotion

## Decision

OBRM v0.10.5 evaluates Realized Capital Flow against forward Bitcoin returns and maximum drawdowns using chronological, no-look-ahead labels. Promotion requires multi-horizon band separation, walk-forward stability, and cross-provider robustness. The decision artifact never changes Composite Risk; implementation requires a separate Composite Risk v2 release.

## Consequences

A provider-equivalence pass is necessary but insufficient. Weak, unstable, or provider-specific evidence remains research-only or not-ready, and negative results remain visible.
