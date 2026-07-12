# OBRM v0.8.0 — Portfolio Layer Alpha

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.8.0`.
- All tests pass.
- Streamlit shows a new `Portfolio Lab` page.
- BTC holdings, cash, DCA, contribution history, target allocation, and permanent core can be configured.
- Recommendation changes between buy, hold, and sell states.
- Purchases cannot exceed available cash.
- DCA-out cannot breach the permanent core.
- Capital-recovery protection can be enabled.

## Commit

```powershell
git add .
git commit -m "Release v0.8.0 - Add Portfolio Layer"
git push origin main
```
