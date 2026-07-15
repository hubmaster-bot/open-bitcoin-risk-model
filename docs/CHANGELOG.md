# Changelog

## v1.0.0-rc.2

- Added SciPy as an explicit runtime dependency for Spearman correlation.
- Split deterministic repository checks from machine-dependent environment checks.
- Excluded local virtual environments from release-tree artifact scanning.
- Prevented the readiness checker from failing on bytecode created by importing the checker itself.
- Added repository-only readiness mode and regression tests for Windows/local-environment behavior.
- Preserved Composite Risk v1 and all evidence-governance boundaries.

## v1.0.0-rc.1

- Added installable PEP 517 project metadata and a console entry point.
- Declared Python 3.11–3.13 support and separated runtime from development dependencies.
- Replaced the UTF-16 environment freeze with a portable runtime dependency specification.
- Added automated release-readiness checks and tests.
- Added an environment-variable template for four live providers without embedding credentials.
- Added the v1.0 release checklist and ADR-034.
- Cleaned release packaging of Git metadata, caches, bytecode, and local-only artifacts.
- Preserved Composite Risk v1 and all evidence-governance boundaries.

## v0.10.5

- Added no-look-ahead future-return and maximum-drawdown labels for capital-flow research.
- Added quantile-band separation tests across 30, 90, 180, and 365-day horizons.
- Added chronological walk-forward stability diagnostics.
- Added cross-provider score robustness gates for Coin Metrics, Glassnode, and CryptoQuant.
- Added formal Promote, Research Only, and Not Ready governance outcomes.
- Added immutable report hashing and JSON persistence.
- Preserved Composite Risk v1 and all live decisions.

## v0.10.4

- Added declared metric mappings for Coin Metrics, Glassnode, CryptoQuant, and CoinGecko.
- Added canonical provider normalization and pairwise equivalence diagnostics.
- Added overlap, coverage, Pearson, Spearman, normalized-MAE, and direction-disagreement gates.
- Added immutable validation-report hashing and JSON persistence.
- Added a research-only Streamlit validation page.
- Explicitly classified CoinGecko market capitalization as a proxy rather than realized-capital equivalence.
- Kept Composite Risk unchanged.


## 0.10.3 — Realized Capital Flow Research

- Added `obrm/research/capital_flow/` as a provider-neutral research module.
- Added ingestion for realized-cap growth/change, realized value flow, capital inflow/outflow, net capital flow, exchange netflow, and documented custom metrics.
- Added provenance metadata, canonical Parquet persistence, and SHA-256 integrity verification.
- Added expanding percentile, 30-day smoothing, 90-day change, yearly percentile, trend direction, acceleration, and Capital Flow Research Score outputs.
- Added validation hooks and a stable validation view for later outcome and multi-provider testing.
- Added the Realized Capital Flow Research Streamlit page.
- Moved Realized Capital Flow from Missing to Research in the Evidence Registry.
- Added ADR-031, Handbook Chapter 17, Developer Guide Chapter 9, and tests.
- Preserved Composite Risk v1 and all live decisions.

## 0.10.2 — Holder Behaviour Research

- Added a provider-neutral daily CSV import pipeline for Holder Behaviour evidence.
- Added canonical schema validation and minimum historical coverage requirements.
- Added explicit provider, definition, licence, source URL, and SHA-256 provenance.
- Added support for dormancy, coin days destroyed, long-term-holder supply, dormant supply, and documented distribution metrics.
- Added no-look-ahead expanding percentiles and 30-day diagnostic scoring.
- Added the Holder Behaviour Research Streamlit page.
- Moved Holder Behaviour from Missing to Research in the Evidence Registry.
- Added holder-behaviour analytics and persistence tests.
- Added ADR-030, Research Handbook Chapter 16, and Developer Guide Chapter 8.
- Preserved validated evidence coverage, Composite Risk v1, and all live decisions.

## 0.10.1 — Fallback Provider Discovery

- Added a structured fallback-provider candidate registry.
- Added candidates for missing Holder Behaviour and Realized Capital Flow evidence.
- Added six-criterion provider assessments covering access, cost, history, definitions, reproducibility, and licensing.
- Added Suitable, Under Review, Unsuitable, Unreviewed, and Future statuses.
- Added local persistence for provider/evidence assessments.
- Added the Fallback Provider Discovery Streamlit page.
- Added provider-discovery and persistence tests.
- Added ADR-029, Research Handbook Chapter 15, and Developer Guide Chapter 7.
- Preserved the canonical Evidence Registry, Composite Risk v1, and all live decisions.

## 0.10.0 — Evidence Registry

- Added a provider-independent Evidence Registry.
- Added canonical evidence and provider-mapping models.
- Added overall, domain, and required-dimension coverage calculations.
- Seeded eight evidence items across On-Chain, Liquidity, Macro, Market Structure, and Sentiment.
- Recorded validated Coin Metrics mappings for MVRV and Hash Rate.
- Recorded provider gaps and future Bitcoin Core paths for missing on-chain evidence.
- Added the Evidence Registry Streamlit page.
- Updated the Documentation Hub and Model Maturity Scorecard.
- Added evidence invariants, coverage, and service tests.
- Added ADR-028, Research Handbook Chapter 14, and Developer Guide Chapter 6.
- Preserved Composite Risk v1 and all live decisions.

## 0.9.5 — On-Chain Promotion Review

- Added a formal promotion-decision engine.
- Added persisted promotion decisions.
- Added Promote, Research Only, and Not Ready outcomes.
- Added explicit separation between validation and live-model changes.
- Added a provider-gap registry for missing on-chain evidence.
- Added the On-Chain Promotion Review Streamlit page.
- Added promotion and provider-gap tests.
- Added ADR-027 and handbook documentation.
- Preserved Composite Risk v1 and all live decisions.
