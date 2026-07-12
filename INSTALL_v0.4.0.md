# OBRM v0.4.0 — Risk Engine Alpha

Copy the release contents over the root of your existing repository.

## Run tests

```powershell
python -m pytest
```

## Refresh data

```powershell
python -m obrm
```

## Launch the dashboard

```powershell
streamlit run app.py
```

## Verify

- Version displays as `0.4.0`.
- Tests pass.
- Dashboard displays BTC price, Price Position Risk, preliminary confidence, and market phase.
- Chart displays BTC price, log-regression fair value, and risk.
- Hover shows date, price, fair value, premium/discount, risk, preliminary confidence, market phase, DCA, and source.
- Research Console displays model diagnostics.

## Commit

```powershell
git add .
git commit -m "Release v0.4.0 - Add Risk Engine Alpha"
git push origin main
```
