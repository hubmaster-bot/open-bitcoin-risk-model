# ADR-027: Separate validation from promotion

## Status

Accepted

## Decision

OBRM v0.9.5 introduces a formal promotion-review artifact after validation.

Validation measures the evidence.

Promotion decides whether that evidence may influence the live model.

## Rule

A successful validation result does not automatically modify Composite Risk.
Promotion requires:

1. a saved decision,
2. visible rationale,
3. a separate implementation release,
4. regression review,
5. updated documentation.

## Current on-chain consequence

The live model remains unchanged unless the formal decision is `promote`.
Incomplete evidence remains research-only or not ready.
