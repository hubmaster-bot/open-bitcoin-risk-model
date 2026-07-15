# Realized Capital Flow Developer Guide

The implementation lives in `obrm/research/capital_flow/`.

- `core.py` defines canonical ingestion, validation, analytics, persistence and integrity verification.
- `paths.py` owns canonical local storage locations.
- `service.py` provides application-level import and load operations.
- `validation_view()` exposes a stable date/score/coverage frame.
- `build_capital_flow_analytics(..., validation_hooks=(... ,))` allows independent validation assertions without coupling the research module to the live model.

Do not add this score to Composite Risk without a separate promotion decision and evidence validation release.
