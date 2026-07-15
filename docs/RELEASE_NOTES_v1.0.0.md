# OBRM v1.0.0 Release Notes

OBRM v1.0.0 is the first stable release of the evidence-first Bitcoin market-risk research and decision-support application.

## Stability baseline

- Composite Risk v1 is unchanged from the validated release-candidate series.
- Research evidence remains isolated from live decisions unless separately promoted and integrated through governance.
- Provider-neutral validation supports Coin Metrics, Glassnode, CryptoQuant, and a deliberately non-equivalent CoinGecko market-cap proxy.
- Capital-flow research includes outcome validation, walk-forward diagnostics, cross-provider robustness, and formal promotion outcomes.

## Release engineering

- Python 3.11–3.13 is supported.
- Runtime and development dependencies are explicitly separated.
- SciPy is included for Spearman correlation.
- Readiness checks support deterministic repository-only execution and platform-independent path handling.
- Release archives exclude local environments, caches, bytecode, Git metadata, and credentials.

## Operational note

Live-provider smoke tests depend on each operator's credentials, subscription tier, rate limits, and deployment environment. Complete the deployment-specific section of `docs/RELEASE_CHECKLIST_v1.0.md` before relying on a production deployment.
