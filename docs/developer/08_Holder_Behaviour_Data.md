# Developer Guide — Holder Behaviour Data

## Canonical schema

- `date`
- `holder_metric_value`
- `provider`
- `provider_metric`
- `metric_kind`
- `definition`
- `licence_note`
- `source_url`

## Import requirements

- daily or daily-normalizable timestamps,
- numeric non-negative values,
- unique sorted dates,
- at least 365 usable rows,
- one metric kind per canonical dataset,
- complete provenance fields.

## Analytics outputs

- expanding percentile,
- 90-day raw-value change,
- raw distribution-risk score,
- 30-day smoothed research score,
- row-level input coverage.

## Provider adapters

A future provider adapter should produce the same canonical schema and call the
same validation and storage functions. Analytics must not depend on a provider's
native field names.
