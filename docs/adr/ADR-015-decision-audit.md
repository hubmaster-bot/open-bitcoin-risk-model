# ADR-015: Make every recommendation auditable

## Status

Accepted

## Decision

OBRM v0.8.5b introduces a Decision Audit containing:

- Market Dimension scores
- standard labels
- weights
- weighted contributions
- Composite Risk
- Model Confidence
- recommendation
- Primary Driver
- template-driven explanation

## Rationale

A recommendation without an audit trail behaves like a black box. The Decision Audit makes every conclusion traceable to visible evidence and calculation steps.

## Primary Driver

The Primary Driver is the Market Dimension with the largest weighted contribution to Composite Risk.
