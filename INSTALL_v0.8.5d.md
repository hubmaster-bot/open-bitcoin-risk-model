# OBRM v0.8.5d — Documentation Foundation

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version is `0.8.5d`.
- All tests pass.
- Streamlit shows a new `Documentation Hub` page.
- User Guide documents appear.
- Research Handbook documents appear.
- Developer Guide documents appear.
- Model Maturity Scorecard appears.
- Documentation files exist under `docs`.

## Commit

```powershell
git add .
git commit -m "Release v0.8.5d - Add Documentation Foundation"
git push origin main
```

## Milestone

This release completes the v0.8.5 explainability series:

- v0.8.5a — Market Dimensions Foundation
- v0.8.5b — Decision Intelligence
- v0.8.5c — Research Experience
- v0.8.5d — Documentation Foundation
