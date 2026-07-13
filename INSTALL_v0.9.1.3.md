# OBRM v0.9.1.3 — Coin Metrics Catalogue Schema Fix

This package contains complete replacement files.

## Install

1. Stop Streamlit with `Ctrl+C`.
2. Extract this ZIP.
3. Copy all contents over the OBRM repository root.
4. Select `Replace files in the destination`.

## Run

```powershell
python -m pytest
streamlit run app.py
```

## Verify

1. Version displays as `0.9.1.3`.
2. All tests pass.
3. Open `On-Chain Data`.
4. Refresh the BTC catalogue.
5. Confirm Bitcoin metrics are listed.
6. Open `On-Chain Analytics`.
7. Refresh selected analytics.

## Commit

```powershell
git add .
git commit -m "Release v0.9.1.3 - Fix Coin Metrics catalogue schema"
git push origin main
```
