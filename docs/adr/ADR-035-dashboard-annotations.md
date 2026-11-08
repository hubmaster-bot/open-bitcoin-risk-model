# ADR-035: Persistent dashboard annotations

## Decision

OBRM v1.1 stores user-created date, price, and risk lines in a local JSON file and renders them as Plotly shapes. The dashboard exposes annotation management beside the chart and keeps the Composite Risk model unchanged.

## Rationale

This provides a practical TradingView-like marking workflow without forcing the Python model into Pine Script or introducing a remote account service.

## Consequences

Annotations are local to the installation, can be exported as JSON or CSV, and do not alter analytics or decision outputs.
