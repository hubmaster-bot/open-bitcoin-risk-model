# OBRM v0.9.1 — On-Chain Analytics

## Release location

Copy this release over the root of the existing OBRM repository.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## In the application

1. Open `On-Chain Data`.
2. Refresh the Coin Metrics BTC catalogue if needed.
3. Open `On-Chain Analytics`.
4. Click `Refresh selected Coin Metrics analytics`.

## Verify

- Version is `0.9.1`.
- All tests pass.
- On-Chain Analytics page appears.
- Required metric identifiers resolve from the local catalogue.
- MVRV, Realized Cap, growth, and diagnostic score appear.
- Optional active supply fails gracefully when unavailable.
- Composite Risk and decisions remain unchanged.

## Commit

```powershell
git add .
git commit -m "Release v0.9.1 - Add On-Chain Analytics"
git push origin main
```
