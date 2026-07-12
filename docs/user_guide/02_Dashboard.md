# User Guide — Understanding the Dashboard

## BTC Price

The most recent validated BTC/USD price in the local canonical dataset.

## Composite Risk

A normalized score between 0 and 1.

- Lower values indicate historically more attractive conditions.
- Higher values indicate historically more elevated conditions.

Composite Risk is not a probability of loss.

## Model Confidence

Indicates how much trust to place in the model's current assessment.

It is based on:

- Coverage
- Agreement
- Data Quality
- Model Maturity

It is not the probability that Bitcoin will rise or fall.

## Market Phase

A plain-English interpretation of the current Composite Risk band.

## Fair Value

The current expanding log-regression fair-value estimate.

## Premium or Discount

The percentage difference between the market price and the fair-value estimate.

## Chart

The main chart combines:

- BTC Price
- Fair Value
- Composite Risk

The native Plotly hover shows the historical model state at a selected date.
