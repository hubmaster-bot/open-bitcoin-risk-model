# OBRM v0.9.1.1 — Coin Metrics Catalogue Hotfix

## Release location

Copy the extracted release contents over the root of the existing OBRM repository, replacing files when prompted.

## Run order

```powershell
python -m pytest
streamlit run app.py
```

Running `python -m obrm` is optional for this hotfix because the market-price pipeline is unchanged.

## Verify

- Version displays as `0.9.1.1`.
- All tests pass.
- Open `On-Chain Data`.
- Click `Refresh Coin Metrics BTC catalogue`.
- The previous HTTP 400 caused by `limit=10000` no longer appears.
- The local catalogue is populated.
- Open `On-Chain Analytics` and refresh the selected metrics.

## Commit the release

```powershell
git add .
git commit -m "Release v0.9.1.1 - Fix Coin Metrics catalogue discovery"
git push origin main
```
