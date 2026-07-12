# Developer Guide — Architecture Overview

OBRM uses a layered architecture.

## Data Layer

Responsible for:

- providers,
- downloads,
- validation,
- provenance,
- storage,
- and freshness.

## Analytics Layer

Responsible for:

- fair value,
- Valuation,
- Momentum,
- Volatility,
- Composite Risk,
- and future Market Dimensions.

## Confidence Layer

Responsible for Model Confidence and its factors.

## Decision Layer

Responsible for:

- thresholds,
- generic DCA decisions,
- Decision Audit,
- and explanations.

## Portfolio Layer

Responsible for applying personal constraints to generic decisions.

## Research Layer

Responsible for:

- backtesting,
- diagnostics,
- walk-forward validation,
- and cycle analysis.

## Presentation Layer

Responsible for Streamlit pages, charts, tables, and documentation views.

Each layer should have one clear responsibility.
