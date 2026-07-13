# OBRM v0.9.0 — On-Chain Data Engine

## Release location

Copy the contents of this release package over the root of your existing OBRM repository, replacing files when prompted.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.9.0`.
- All tests pass.
- Streamlit shows a new `On-Chain Data` page.
- Clicking `Refresh Coin Metrics BTC catalogue` saves the local capability catalogue.
- Metric names, frequencies, and coverage appear.
- No On-Chain Market Dimension is added yet.
- Existing Composite Risk and Decision Engine outputs remain unchanged.

## Commit the release

```powershell
git add .
git commit -m "Release v0.9.0 - Add On-Chain Data Engine"
git push origin main
```

## Roadmap

- v0.9.0 — On-Chain Data Engine
- v0.9.1 — On-Chain Analytics
- v0.9.2 — On-Chain Market Dimension and Composite Risk v2
- v0.9.3 — Validation and documentation
