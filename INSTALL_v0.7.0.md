# OBRM v0.7.0 — Walk-Forward Validation Alpha

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.7.0`.
- All tests pass.
- Streamlit shows a new `Validation Lab` page.
- 90-, 365-, and 730-day horizons are available.
- Median forward returns display by risk band.
- Negative 365-day outcome frequencies display.
- Confidence filtering works.
- Cycle stability appears.

## Commit

```powershell
git add .
git commit -m "Release v0.7.0 - Add Walk-Forward Validation"
git push origin main
```
