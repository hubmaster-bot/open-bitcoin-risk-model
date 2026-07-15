# v1.0 Release Candidate Checklist

## Automated gates

- [x] Version is `1.0.0-rc.1`.
- [x] Runtime and development dependencies are separated.
- [x] Package metadata declares Python 3.11–3.13 support.
- [x] Full unit test suite passes.
- [x] All Python source and Streamlit pages compile.
- [x] Editable clean install succeeds without importing the source tree implicitly.
- [x] Release archive excludes Git metadata, caches, bytecode, local environments, and real credentials.
- [x] Composite Risk v1 is unchanged.

## Local/manual gates before final v1.0.0

- [ ] Launch `streamlit run app.py` and inspect every page.
- [ ] Run Coin Metrics smoke test with the intended production access tier.
- [ ] Run Glassnode smoke test with the intended production access tier.
- [ ] Run CryptoQuant smoke test with the intended production access tier.
- [ ] Run CoinGecko smoke test and confirm it remains a market-cap proxy.
- [ ] Verify rate-limit and error messages with invalid/expired credentials.
- [ ] Confirm no provider keys are present in Git history, logs, screenshots, fixtures, or exported reports.
- [ ] Complete the final governance review of all promoted and research-only evidence.
- [ ] Tag `v1.0.0` only after all manual gates pass.

## Release rule

A release candidate may become v1.0.0 without feature changes. Any change to Composite Risk, evidence weights, promotion status, or live decision behaviour requires a separate reviewed release.
