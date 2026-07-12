# OBRM v0.8.5a — Market Dimensions Foundation

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.8.5a`.
- All tests pass.
- Streamlit shows a new `Model Intelligence` page.
- The page displays Market Dimension cards for Valuation, Momentum, and Volatility.
- Every card shows score, standard label, explanation, weight, and contribution.
- Model Confidence displays Coverage, Agreement, Data Quality, and Model Maturity.
- Documentation appears under `docs/handbook`.

## Commit

```powershell
git add .
git commit -m "Release v0.8.5a - Add Market Dimensions foundation"
git push origin main
```
