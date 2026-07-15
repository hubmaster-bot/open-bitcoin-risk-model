# ADR-029: Separate provider discovery from provider approval

## Status

Accepted

## Decision

OBRM v0.10.1 introduces a structured fallback-provider discovery process.

A provider candidate is not an active provider mapping. It must be reviewed for:

- access,
- free-tier availability,
- historical coverage,
- metric definition,
- reproducibility,
- licensing.

Only a candidate that passes every criterion may be marked suitable. A suitable
assessment still requires a separate provider-adapter and data-validation
release before the provider can satisfy evidence in the canonical registry.

## Rationale

The Coin Metrics work demonstrated that catalogue presence, apparent public
access, and actual usable data are different facts. Provider discovery therefore
must remain an explicit research stage rather than an assumption.
