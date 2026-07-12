# OBRM v0.4.1 — Research Inspector

Copy the release contents over the repository root.

## Manual change required

In `obrm/dashboard/app.py`, replace the current Plotly chart call with the custom component described below, or use the complete replacement file from this release if present.

## Run

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.4.1`.
- Fair value is solid `#2ECC71`.
- All three lines remain on one chart.
- Hover updates the fixed Research Inspector.
- The large floating tooltip no longer covers the chart.

## Commit

```powershell
git add .
git commit -m "Release v0.4.1 - Add Research Inspector"
git push origin main
```
