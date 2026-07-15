# Changelog

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
