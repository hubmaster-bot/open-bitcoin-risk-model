# v1.0.0 Release Checklist

## Automated release gates

- [x] Application version and package metadata are `1.0.0`.
- [x] Runtime and development dependencies are separated.
- [x] SciPy is declared for Spearman correlation.
- [x] Package metadata declares Python 3.11–3.13 support.
- [x] Full unit test suite passes.
- [x] All Python source and Streamlit pages compile.
- [x] Wheel build and clean wheel import succeed.
- [x] Release archive excludes Git metadata, caches, bytecode, local environments, and real credentials.
- [x] Readiness tests are platform independent.
- [x] Composite Risk v1 is unchanged.

## Deployment-specific operational checks

These checks depend on the deployment environment, provider subscriptions, and credentials. They are not embedded in or required to inspect the source archive.

- [ ] Launch `streamlit run app.py` and inspect every page in the target deployment environment.
- [ ] Run Coin Metrics smoke tests with the intended access tier.
- [ ] Run Glassnode smoke tests with the intended access tier.
- [ ] Run CryptoQuant smoke tests with the intended access tier.
- [ ] Run CoinGecko smoke tests and confirm it remains classified as a market-cap proxy.
- [ ] Verify rate-limit and invalid/expired-credential messages.
- [ ] Confirm no provider keys are present in Git history, logs, screenshots, fixtures, or exported reports.

## Governance invariant

Any future change to Composite Risk, evidence weights, promotion status, or live decision behaviour requires a separate reviewed release.
