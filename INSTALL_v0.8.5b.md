# OBRM v0.8.5b — Decision Intelligence

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.8.5b`.
- All tests pass.
- Streamlit shows a new `Decision Intelligence` page.
- Decision Audit displays Composite Risk, Model Confidence, Decision, and Primary Driver.
- Market Dimension table displays scores, weights, and contributions.
- Contribution Breakdown chart appears.
- Explain This Decision displays a deterministic explanation.
- Decision Threshold table appears.
- New handbook chapters appear under `docs/handbook`.

## Commit

```powershell
git add .
git commit -m "Release v0.8.5b - Add Decision Intelligence"
git push origin main
```
