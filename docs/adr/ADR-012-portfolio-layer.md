# ADR-012: Add a constraint-aware Portfolio Layer

## Status

Accepted

## Decision

OBRM v0.8.0 translates generic market decisions into portfolio-aware guidance using user-entered constraints.

## Inputs

- BTC holdings
- Cash available
- Normal weekly DCA
- Total contributed capital
- Target BTC allocation
- Permanent BTC core
- Optional capital-recovery limit

## Rationale

A generic market signal cannot determine an appropriate transaction without knowing the user's current holdings and constraints. The Portfolio Layer separates market assessment from personal execution.

## Safeguards

- Purchases cannot exceed available cash.
- DCA-out cannot reduce holdings below the permanent core.
- Low-confidence signals cannot trigger active transactions.
- Optional capital recovery limits sales to unrecovered contributed capital.

## Limitations

The Portfolio Layer does not yet include taxes, fees, debt, income, emergency reserves, jurisdiction, or personal suitability.
