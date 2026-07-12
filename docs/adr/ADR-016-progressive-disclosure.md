# ADR-016: Use progressive disclosure for model detail

## Status

Accepted

## Decision

OBRM v0.8.5c introduces three display modes:

- Executive
- Analyst
- Research

Each mode reveals more detail without changing the underlying calculations.

## Rationale

Different users need different levels of information. A quick market check should not require reading raw calculations, while research users should be able to inspect every input, weight, contribution, and methodology note.

## Interaction decision

Historical exploration uses native Plotly unified hover. Custom iframe pointer and click interactions remain excluded because they proved unreliable in Streamlit.
