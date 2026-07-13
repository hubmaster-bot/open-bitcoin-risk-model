# OBRM v0.9.2 — Community Metric Validator

## Release location

Copy the extracted contents over the root of the existing OBRM repository.

## Run

```powershell
python -m pytest
streamlit run app.py
```

## In OBRM

1. Open `On-Chain Data` and confirm the Coin Metrics BTC catalogue exists.
2. Open `Community Metric Validator`.
3. Run the validator with the default research search terms.
4. Review available and forbidden metrics.
5. Open `On-Chain Analytics`.
6. Refresh analytics only after required inputs appear as available.

## Verify

- Version displays as `0.9.2`.
- All tests pass.
- The Community Metric Validator page appears.
- The verified registry is saved locally.
- HTTP 403 metrics are marked forbidden rather than crashing the app.
- On-chain selection uses only verified available metrics.

## Commit

```powershell
git add .
git commit -m "Release v0.9.2 - Add Community Metric Validator"
git push origin main
```
