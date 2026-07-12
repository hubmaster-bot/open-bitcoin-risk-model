# ADR-006: Use a fixed Research Inspector

## Status

Accepted

## Decision

The main chart keeps Bitcoin price, fair value, and risk together. Historical detail moves from a floating tooltip into a fixed right-hand Research Inspector.

## Rationale

- Preserves the immediate visual relationship between price and risk.
- Prevents the tooltip from obscuring the chart.
- Creates room for more fields in future releases.
- Improves historical exploration on large displays.

## Styling

The fair-value line uses `#2ECC71`, remains solid, and keeps a restrained width.
