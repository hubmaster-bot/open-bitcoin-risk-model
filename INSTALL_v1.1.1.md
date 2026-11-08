# Install OBRM v1.1.1

OBRM supports Python 3.11–3.13. Python 3.13 is recommended on Windows.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
python -m pytest
python -m obrm
python -m streamlit run app.py
```

Expected automated result: `147 passed`. `python -m obrm` refreshes the daily Bitcoin dataset; the Streamlit command launches the dashboard.

Chart annotations are stored locally at `data/user/chart_annotations.json`. Back up that file before replacing an existing installation when you want to retain personal lines.
