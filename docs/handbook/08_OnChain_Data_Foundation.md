# Research Handbook — On-Chain Data Foundation

## Purpose

Price describes what the market is doing.

On-chain data can provide evidence about network activity, realized valuation, transferred supply, holder behaviour, and capital movement.

## v0.9.0 boundary

Version 0.9.0 adds infrastructure only.

It does not yet:

- select final metrics,
- calculate an On-Chain score,
- change Composite Risk,
- change Decision Engine outputs.

## Provider

The initial provider is Coin Metrics Community.

## Capability-first process

OBRM discovers the exact BTC metric catalogue and stores:

- metric identifiers,
- supported frequencies,
- minimum time,
- maximum time,
- descriptions where supplied,
- provider provenance.

## Canonical dataset

Selected metrics will later be normalized into a local daily Parquet dataset with metadata, freshness, gap detection, and SHA-256 integrity.
