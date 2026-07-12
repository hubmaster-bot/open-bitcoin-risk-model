# Developer Guide — Data Flow

## Primary flow

1. Provider downloads raw market data.
2. Validator checks structure and values.
3. Fusion engine creates canonical daily history.
4. Storage writes Parquet and metadata.
5. Analytics calculate no-look-ahead Market Dimensions.
6. Composite Risk combines dimension scores.
7. Model Confidence evaluates trust in the assessment.
8. Decision Engine produces a generic recommendation.
9. Portfolio Layer applies user constraints.
10. Research tools evaluate historical behaviour.

## Validation boundary

Future-return columns must never enter the analytics or decision pipeline.

They belong only in the research validation layer as outcome labels.
