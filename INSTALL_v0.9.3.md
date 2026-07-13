# OBRM v0.9.3 — Validated On-Chain Research Layer

## Release location

Copy the extracted contents over the root of the existing OBRM repository.

## Run

```powershell
python -m pytest
streamlit run app.py
```

## In OBRM

1. Open `Community Metric Validator` and confirm:
   - `CapMVRVCur` is available.
   - `HashRate` is available.
2. Open `Validated On-Chain Research`.
3. Click `Refresh validated on-chain dataset`.
4. Review MVRV, hash-rate growth, evidence coverage, and the diagnostic score.

## Verify

- Version displays as `0.9.3`.
- All tests pass.
- The Validated On-Chain Research page appears.
- Dataset refresh requests only `CapMVRVCur` and `HashRate`.
- Evidence coverage shows `2 of 4`.
- Composite Risk and decisions remain unchanged.

## Commit

```powershell
git add .
git commit -m "Release v0.9.3 - Add Validated On-Chain Research Layer"
git push origin main
```
