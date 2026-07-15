# OBRM v0.10.2 — Holder Behaviour Research

## Install

1. Stop Streamlit with `Ctrl+C`.
2. Extract the release patch.
3. Copy its contents over the OBRM repository root.
4. Replace destination files when prompted.

## Run

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## In OBRM

1. Open `Holder Behaviour Research`.
2. Import a reviewed daily CSV.
3. Select the date and value columns.
4. Record the provider, metric definition, licence, and metric kind.
5. Review the diagnostic score and stored provenance.

## Verify

- Version displays as `0.10.2`.
- All tests pass.
- Holder Behaviour Research appears in Streamlit.
- Inputs shorter than 365 rows are rejected.
- Provenance metadata and SHA-256 are stored.
- Evidence Registry shows Holder Behaviour as Research.
- Overall validated coverage remains unchanged.
- Composite Risk v1 and live decisions remain unchanged.

## Commit

```powershell
git add .
git commit -m "Release v0.10.2 - Add Holder Behaviour Research"
git push origin main
```
