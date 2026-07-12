# ADR-007: Polish the Research Inspector without changing the chart model

## Status

Accepted

## Decision

OBRM v0.4.2 keeps Bitcoin price, fair value, and risk on one chart while improving presentation:

- Separate title and legend spacing.
- Widen the Research Inspector.
- Add restrained monochrome symbols beside labels.
- Keep confidence percentages primary, with colour used only as a secondary cue.
- Add concise model notes and explicit limitations.

## Rationale

The combined chart best preserves the visual relationship between price and risk. The inspector should improve readability without turning into decorative UI or hiding uncertainty.
