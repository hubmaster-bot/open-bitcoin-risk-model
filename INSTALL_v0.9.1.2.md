# OBRM v0.9.1.2 — Coin Metrics Provider Maintenance

This package contains complete replacement files. Do not splice individual
functions into the existing files.

## Install

1. Stop Streamlit with `Ctrl+C`.
2. Extract this package.
3. Copy its contents over the OBRM repository root.
4. Choose **Replace files in the destination** when prompted.

## Run

```powershell
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.9.1.2`.
- Test collection completes without an `IndentationError`.
- All tests pass.
- Open `On-Chain Data`.
- Click `Refresh Coin Metrics BTC catalogue`.
- The request contains neither `assets` nor `limit`.
- The local BTC catalogue is created.
- Open `On-Chain Analytics` and refresh the selected metrics.

## Commit

```powershell
git add .
git commit -m "Release v0.9.1.2 - Stabilize Coin Metrics provider"
git push origin main
```
