# OBRM v0.9.4 — On-Chain Validation Lab

## Install

1. Stop Streamlit with `Ctrl+C`.
2. Extract this release.
3. Copy all contents over the OBRM repository root.
4. Replace destination files when prompted.

## Run

```powershell
python -m pytest
streamlit run app.py
```

## Prerequisite

The validated on-chain dataset from v0.9.3 must exist.

If necessary:

1. Open `Validated On-Chain Research`.
2. Click `Refresh validated on-chain dataset`.

## Verify

- Version displays as `0.9.4`.
- All tests pass.
- `On-Chain Validation` appears.
- Forward-return bucket analysis loads.
- Correlation matrix loads.
- Composite Risk v1 and Research Composite v2 are compared.
- Readiness shows the visible promotion result.
- Live decisions remain unchanged.

## Commit

```powershell
git add .
git commit -m "Release v0.9.4 - Add On-Chain Validation Lab"
git push origin main
```
