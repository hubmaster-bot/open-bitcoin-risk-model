# OBRM v0.4.3 — Interaction Stabilisation

Copy the release contents over the root of the existing repository.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.4.3`.
- Legend sits above the chart without overlap.
- Clicking anywhere inside the plot selects the nearest date.
- The Research Inspector updates after a click.
- A vertical dotted line locks to the selected date.
- The latest date is selected when the chart first loads.
- Inspector icons remain.
- All tests pass.

## Commit

```powershell
git add .
git commit -m "Release v0.4.3 - Stabilise chart interaction"
git push origin main
```
