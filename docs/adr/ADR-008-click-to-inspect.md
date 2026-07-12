# ADR-008: Use click-to-inspect with a locked crosshair

## Status

Accepted

## Decision

OBRM replaces unreliable pointer-following behaviour with a stable click-to-inspect interaction.

A click within the plotting area:

1. selects the nearest historical date,
2. updates the Research Inspector, and
3. locks a vertical dotted crosshair to that date.

## Rationale

The Streamlit embedded-component environment did not reliably deliver continuous pointer movement across browsers and layouts. Click-to-inspect is deterministic, easier to test, and better suited to deliberate historical research.

## Scope

This is the final UI stabilisation release before work resumes on the multi-factor risk and decision engines.
