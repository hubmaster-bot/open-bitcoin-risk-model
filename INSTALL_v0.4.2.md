# OBRM v0.4.2 — Inspector Polish

Copy the release contents over the root of the existing repository.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.4.2`.
- Title and legend no longer overlap.
- Research Inspector is wider.
- Symbols remain restrained and monochrome.
- Confidence still displays as a percentage.
- Confidence percentage colour changes by confidence level.
- Model Notes appear below the inspector metrics.
- Fair value remains solid `#2ECC71`.
- All tests pass.

## Commit

```powershell
git add .
git commit -m "Release v0.4.2 - Polish Research Inspector"
git push origin main
```
