# Portfolio Lab

## Purpose

The Portfolio Lab answers:

> Given the current OBRM decision and my current holdings, what would one portfolio-aware action look like?

## Separation of responsibilities

### Risk Engine

Describes market conditions.

### Decision Engine

Produces a generic DCA-in, hold, pause, or DCA-out action.

### Portfolio Layer

Applies personal constraints:

- available cash,
- current allocation,
- target allocation,
- permanent core,
- contribution history.

## Capital recovery

Users may optionally limit DCA-out sales to unrecovered contributed capital. This supports a strategy where only original capital is gradually recovered while a core BTC position remains invested.

## Important limitation

This remains a research planning tool. It is not personalised financial, tax, or legal advice.
