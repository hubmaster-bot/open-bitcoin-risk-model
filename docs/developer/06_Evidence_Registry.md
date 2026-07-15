# Developer Guide — Evidence Registry

## Package

The provider-independent registry lives in `obrm/evidence/`.

- `models.py` defines evidence and provider-mapping dataclasses.
- `registry.py` contains the canonical immutable seed registry.
- `coverage.py` calculates overall, domain, and required-dimension coverage.
- `service.py` provides read-only lookup functions for application code.

## Adding evidence

A new evidence item must have:

- a unique stable key,
- a unique display name,
- a research domain,
- an intended Market Dimension,
- a plain-English purpose,
- a supported status,
- documentation,
- and an explicit statement of whether it is required.

## Adding a provider mapping

Provider-specific information belongs in `PROVIDER_MAPPINGS`, not in the
logical evidence item. Each mapping records its metric definition and
provenance so similarly named provider metrics are not assumed equivalent.

## Validation rule

An evidence item marked `validated` must have at least one provider mapping
marked `validated`. Tests enforce this invariant.

## Stability

Evidence keys are public research identifiers. Renaming provider metrics must
not require renaming an evidence key unless the underlying economic question
has changed.
