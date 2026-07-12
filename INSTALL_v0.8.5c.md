# OBRM v0.8.5c — Research Experience

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.8.5c`.
- All tests pass.
- Streamlit shows a new `Research Experience` page.
- Executive, Analyst, and Research modes are available.
- Native Plotly hover displays the historical research snapshot.
- Analyst mode shows Market Dimensions, contributions, confidence, and explanation.
- Research mode shows raw calculations and methodology.
- Fair value remains solid `#2ECC71`.
- Legend sits above the chart.

## Commit

```powershell
git add .
git commit -m "Release v0.8.5c - Add Research Experience"
git push origin main
```
