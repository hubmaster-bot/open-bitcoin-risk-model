# Capital Flow Outcome Validation

`obrm.research.capital_flow_validation` consumes dated Bitcoin prices and the provider-neutral Capital Flow Research Score. It creates future-return and future-maximum-drawdown labels only for evaluation, never as model inputs.

The report covers 30, 90, 180, and 365-day horizons, quantile-band separation, chronological walk-forward windows, and provider-score rank correlation. Its promotion decision is governance metadata. `live_model_changed` is always false in v0.10.5.
