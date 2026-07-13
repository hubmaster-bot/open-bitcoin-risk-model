# Research Handbook — Community Metric Validation

## Why validation is required

A provider catalogue can show that a metric exists without granting access to
that metric under the current subscription or Community tier.

## OBRM process

1. Discover the provider catalogue.
2. Select candidate metrics.
3. Request a small daily sample for each metric.
4. Classify the result.
5. Save a verified local availability registry.
6. Allow analytics to use only metrics marked available.

## Status meanings

- **Available:** a real Community API download returned usable observations.
- **Forbidden:** the provider returned HTTP 401 or 403.
- **Empty:** the request succeeded but no usable values were returned.
- **Error:** another provider or network error occurred.
- **Skipped:** the catalogue did not advertise the required frequency.

## Provider independence

A forbidden Coin Metrics metric may later be supplied by another provider or
computed from Bitcoin Core. The logical metric and provider provenance remain
separate.
