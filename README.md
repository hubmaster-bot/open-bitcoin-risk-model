# Open Bitcoin Risk Model (OBRM)

OBRM is an evidence-first Bitcoin market-risk research and decision-support application. It combines market dimensions, validation tooling, explainability, portfolio research, on-chain evidence governance, and provider-neutral capital-flow research in a Streamlit interface.

## Release status

This archive is **v1.0.0**, the first stable OBRM release. Composite Risk v1 remains unchanged. Research evidence cannot affect live decisions without a separate, documented promotion and model-design release.

## Supported Python

Python 3.11, 3.12, and 3.13 are supported.

## Install

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
streamlit run app.py
```

Optional provider credentials are documented in `.env.example`. Real keys must remain outside source control.

## Release verification

```bash
python -m obrm.release.readiness
python -m compileall -q obrm pages app.py
python -m pytest
```

See `docs/RELEASE_CHECKLIST_v1.0.md` for live-provider and UI checks that require local credentials or manual inspection.
