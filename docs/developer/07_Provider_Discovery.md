# Developer Guide — Provider Discovery

## Modules

- `obrm/evidence/provider_discovery.py` — candidates and assessment rules
- `obrm/evidence/discovery_store.py` — local assessment persistence
- `obrm/evidence/discovery_paths.py` — local registry path
- `obrm/evidence/discovery_service.py` — presentation-layer service

## Design rules

- Candidate metadata must not be imported by live analytics.
- No candidate starts as suitable.
- URLs and access claims are research notes until confirmed.
- Assessment data is local and reproducible.
- Provider adapters require a separate release.
- Evidence keys must already exist in the canonical Evidence Registry.

## Adding a candidate

Register:

- stable key,
- display name,
- provider type,
- candidate status,
- supported logical evidence keys,
- proposed access method,
- expected cost status,
- source and documentation URLs where known,
- research notes,
- priority.

Add tests for uniqueness, ordering, and evidence-key compatibility.
