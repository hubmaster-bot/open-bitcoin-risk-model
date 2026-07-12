# OBRM v0.3.4 — Foundation Complete

Copy the release contents over the root of your existing repository.

## Run the data fusion refresh

```powershell
python -m obrm
```

The log should show both Coin Metrics Community and Yahoo Finance being fetched, followed by a fused coverage range.

## Run tests

```powershell
python -m pytest
```

## Launch the application

```powershell
streamlit run app.py
```

## Verify

- Dashboard version is `0.3.4`.
- Latest date is current or close to current.
- Research Console shows freshness status.
- Research Console shows source-provenance segments.
- Feature Registry appears.
- Tests pass.

## Commit

```powershell
git add .
git commit -m "Release v0.3.4 - Complete data foundation"
git push origin main
```
