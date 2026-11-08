# OBRM v1.1.1 release checklist

- [ ] Python 3.11–3.13 environment
- [ ] `python -m pip install -e ".[dev]"`
- [ ] `python -m pytest` reports 147 passed
- [ ] Price annotation label appears beside its line
- [ ] Risk annotation label appears at its selected risk level
- [ ] Show/Hide toggle persists across refreshes
- [ ] Price axis uses explicit USD labels
- [ ] `obrm-release-check --repository-only` passes after cache cleanup
- [ ] Streamlit dashboard launches successfully
- [ ] Release archive contains no `.venv`, caches, bytecode, or credentials
