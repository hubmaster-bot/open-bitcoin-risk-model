# ADR-011: Validate OBRM with time-ordered outcome labels

## Status

Accepted

## Decision

OBRM v0.7.0 evaluates historical risk values against later returns while preserving a strict separation between model inputs and validation outcomes.

The risk series is calculated first using no-look-ahead analytics. Forward returns are then added only as outcome labels.

## Measures

- Median and mean forward returns
- Positive-outcome frequency
- Worst and best outcomes
- Frequency of negative 365-day outcomes
- Risk/return monotonicity
- Behaviour across broad historical eras

## Limitations

- Forward-return windows overlap.
- The number of independent Bitcoin cycles is small.
- Historical relationships may not persist.
- Threshold and horizon selection can influence conclusions.
