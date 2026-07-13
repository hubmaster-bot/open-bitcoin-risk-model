# Developer Guide — Research Data Providers

## Provider contract

Every provider must support:

- capability discovery,
- time-series fetch,
- schema normalization,
- provenance,
- validation,
- local storage.

## Canonical schema

A canonical research dataset contains:

- `date`
- one or more metric columns
- `provider`
- `asset`

Provider-specific pagination and response fields remain inside the adapter.

## Failure behaviour

The engine should fail clearly when:

- no metrics are requested,
- no observations are returned,
- required columns are missing,
- all values for a requested metric are unavailable,
- dates are invalid or duplicated.

## Analytics isolation

Analytics modules must consume canonical local datasets rather than make direct network requests.
