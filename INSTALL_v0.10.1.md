# OBRM v0.10.1 — Fallback Provider Discovery

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

## Verify

- Version displays as `0.10.1`.
- All tests pass.
- `Fallback Provider Discovery` appears in Streamlit.
- Holder Behaviour and Realized Capital Flow show ordered provider candidates.
- Provider assessments can be saved locally.
- No candidate is automatically promoted into the canonical provider mappings.
- Composite Risk v1 and live decisions remain unchanged.

## Commit

```powershell
git add .
git commit -m "Release v0.10.1 - Add Fallback Provider Discovery"
git push origin main
```
