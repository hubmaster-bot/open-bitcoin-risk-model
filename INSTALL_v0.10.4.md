# Install OBRM v0.10.4

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

Open **Multi-Provider Validation** and upload reviewed daily CSV exports with `date` and `value` columns. No API keys are included in the repository. Provider credentials, when live adapters are added, must be supplied through environment variables.
