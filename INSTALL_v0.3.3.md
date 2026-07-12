# OBRM v0.3.3 installation

Copy this release over the root of your existing repository.

## Run

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

The first command should try Coin Metrics Community first, then Yahoo Finance, then Bitstamp.

## Verify

- Dates display as `DD-Mon-YYYY`.
- The dashboard sidebar contains Dashboard and Research Console.
- The Research Console shows rows, date coverage, missing calendar days, provider, and file hash.
- The dashboard contains configurable Dynamic DCA controls.
- Tests pass.

## Commit

```powershell
git add .
git commit -m "Release v0.3.3 - Add historical data and Research Console"
git push origin main
```
