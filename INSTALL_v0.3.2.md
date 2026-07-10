# OBRM v0.3.2 installation

Copy the folders and files from this release into the root of your existing repository, allowing Windows to replace files when prompted.

## Important cleanup

Your earlier `coingecko.py` file may still contain Yahoo code. It is no longer imported by v0.3.2, so it can remain temporarily, but it should be removed in a later cleanup release.

## Run the data update

From the VS Code terminal with `(.venv)` active:

```powershell
python -m obrm
```

The configured primary provider is Yahoo Finance, with Bitstamp as fallback. This preserves your currently working pipeline while the new engine is introduced safely.

## Run tests

```powershell
pytest
```

## Run the dashboard

```powershell
streamlit run app.py
```

Displayed dates should now use `DD-Mon-YYYY`.

## Switching the primary provider

In `obrm/core/config.py`, change:

```python
primary_provider: str = "yahoo"
```

to:

```python
primary_provider: str = "bitstamp"
```

Then run `python -m obrm` again.

Bitstamp's API may not provide its entire exchange history consistently through this endpoint. Provider coverage is therefore treated as a property to validate, not an assumption.

## Suggested commit

```powershell
git add .
git commit -m "Release v0.3.2 - Add Market Data Engine"
git push origin main
```
