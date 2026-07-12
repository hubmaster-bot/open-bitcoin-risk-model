# OBRM v0.6.0 — Backtesting and Validation Alpha

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.6.0`.
- All tests pass.
- Sidebar contains `Backtesting Lab`.
- Fixed DCA and OBRM dynamic wealth are compared.
- Weekly contribution and start date can be changed.
- Dynamic allocation displays BTC and cash.
- Strategy summary and action diagnostics appear.
- The app warns that fees, taxes, spread, and slippage are excluded.

## Commit

```powershell
git add .
git commit -m "Release v0.6.0 - Add Backtesting Lab"
git push origin main
```
