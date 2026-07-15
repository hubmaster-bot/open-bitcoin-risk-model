# Install OBRM v1.0.0-rc.1

1. Install Python 3.11, 3.12, or 3.13.
2. Create and activate a virtual environment.
3. Run `python -m pip install --upgrade pip`.
4. Run `python -m pip install -e ".[dev]"`.
5. Run `python -m pytest`.
6. Run `python -m obrm.release.readiness`.
7. Launch with `streamlit run app.py`.

Copy `.env.example` to `.env` only when live-provider credentials are needed. Never commit `.env` or real keys.
