# ADR-034: v1 Release Hardening and Reproducible Packaging

## Status

Accepted for v1.0.0-rc.1.

## Decision

OBRM uses PEP 517 project metadata, explicit Python support, separated runtime/development dependencies, automated readiness checks, credential placeholders, and a clean source archive. Release-candidate hardening must not change Composite Risk v1 or silently promote research evidence.

## Consequences

Installation is reproducible at the declared compatibility level, release archives are smaller and safer, and manual live-provider checks remain explicit because credentials and subscription entitlements cannot be validated in an offline build.
