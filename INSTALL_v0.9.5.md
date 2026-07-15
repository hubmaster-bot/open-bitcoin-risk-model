# OBRM v0.9.5 — On-Chain Promotion Review

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

## Prerequisites

- The validated v0.9.3 on-chain dataset must exist.
- The v0.9.4 validation report must be able to build.

## In OBRM

1. Open `On-Chain Promotion Review`.
2. Click `Run formal promotion review`.
3. Review the decision, rationale, and provider gaps.

## Verify

- Version displays as `0.9.5`.
- All tests pass.
- The promotion-review page appears.
- A local JSON decision is saved.
- The page explicitly states that the live model was not changed.
- Composite Risk v1 remains active.

## Commit

```powershell
git add .
git commit -m "Release v0.9.5 - Add On-Chain Promotion Review"
git push origin main
```
