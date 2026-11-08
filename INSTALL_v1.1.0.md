# OBRM v1.1.0 installation

Use Python 3.11–3.13.

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

`python -m obrm` refreshes the daily data. The Streamlit command launches the dashboard.
Chart annotations are stored in `data/user/chart_annotations.json`.
