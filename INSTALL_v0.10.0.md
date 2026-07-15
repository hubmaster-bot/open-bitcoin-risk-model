# OBRM v0.10.0 — Evidence Registry

This release was built against the uploaded v0.9.5 repository.

## Install

1. Stop Streamlit with `Ctrl+C`.
2. Back up the repository or confirm the current work is committed.
3. Extract the release package.
4. Copy the extracted contents over the OBRM repository root.
5. Replace destination files when prompted.

## Run

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.10.0`.
- The full test suite passes.
- A new `Evidence Registry` page appears.
- Overall coverage shows `2 of 8` or `25%`.
- Required On-Chain coverage shows `2 of 4` or `50%`.
- Realized Valuation and Network Strength show validated Coin Metrics mappings.
- Holder Behaviour and Realized Capital Flow show provider gaps and fallback paths.
- Composite Risk v1 and all live decisions remain unchanged.

## Commit

```powershell
git add .
git commit -m "Release v0.10.0 - Add Evidence Registry"
git push origin main
```
