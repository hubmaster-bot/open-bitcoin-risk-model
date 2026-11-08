# OBRM v1.1.1 — Chart Annotation Polish and Windows Maintenance

OBRM v1.1.1 refines the v1.1 chart workspace without changing Composite Risk v1.

## Fixed

- Price-line labels now remain attached to the BTC price axis.
- Risk-line labels now remain attached to their selected risk level.
- Logarithmic price ticks now show complete USD magnitudes.
- Windows path handling in the source-cache regression test is platform-independent.

## Added

- Persistent Show/Hide toggles for every saved annotation.
- Clearer release-check messaging when local development caches are present.
- Improved title and legend separation on constrained dashboard widths.

Personal annotations remain stored in `data/user/chart_annotations.json`.
