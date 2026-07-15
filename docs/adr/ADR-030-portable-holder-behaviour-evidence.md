# ADR-030: Introduce portable Holder Behaviour evidence

## Status

Accepted

## Decision

OBRM v0.10.2 introduces a provider-neutral daily CSV pipeline for Holder
Behaviour research.

The importer requires explicit provider, metric definition, licence note, metric
kind, and source provenance. Data is normalized into one canonical daily schema
and stored locally with a SHA-256 hash.

## Supported evidence forms

- dormancy,
- coin days destroyed,
- long-term-holder supply percentage,
- dormant supply percentage,
- a documented custom distribution metric.

## Scoring direction

Higher dormancy, coin-days-destroyed, or distribution values imply more old-coin
spending and therefore a higher research score.

Higher long-term-holder or dormant-supply percentages imply stronger conviction,
so their percentile is inverted.

## Boundary

The resulting score is research-only. It does not alter Composite Risk, Model
Confidence, decisions, Portfolio Lab, or live backtests.
