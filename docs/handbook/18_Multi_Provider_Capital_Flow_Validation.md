# Multi-Provider Capital-Flow Validation

v0.10.4 tests whether independently sourced capital-flow evidence behaves consistently after explicit normalization.

The validation compares Coin Metrics, Glassnode, and CryptoQuant metrics when they can be mapped to the same realized-capital definition. CoinGecko is supported as a market-cap proxy source, but its market-cap series is not automatically equivalent to realized capitalization.

Each comparison reports historical overlap, coverage, linear and rank correlation, normalized error, and disagreement in day-to-day direction. A failure is evidence to investigate definitions, units, timestamps, revisions, and provider methodology—not a reason to silently select one source.

This release does not alter the live Composite Risk model. Promotion remains a separate decision.
