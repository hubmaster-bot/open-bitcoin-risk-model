# Developer Guide — Adding a Market Dimension

A new Market Dimension should not be added merely because data is available.

## Requirements

A proposed dimension must:

- answer a distinct market question,
- use documented inputs,
- have a normalized 0–1 score,
- avoid look-ahead bias,
- include tests,
- include plain-English explanations,
- define confidence behaviour,
- and improve validation evidence.

## Registration

Add metadata to the Market Dimension registry:

- key
- display name
- weight
- score column
- description

## Required updates

- analytics calculation
- Composite Risk configuration
- Model Confidence coverage
- Decision Audit
- historical hover
- Validation Lab
- Backtesting
- Research Handbook
- ADR
- tests
