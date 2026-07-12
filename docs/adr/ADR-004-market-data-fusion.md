# ADR-004: Fuse historical and live BTC price sources

## Status

Accepted

## Decision

OBRM will build its canonical BTC/USD daily series by combining:

- Coin Metrics Community for deep historical coverage.
- Yahoo Finance for fresher daily market data.
- Bitstamp only as a final fallback when the preferred sources fail.

On overlapping dates, the live source wins.

## Rationale

No single free source currently provides both the deepest practical history and consistently current daily data. Fusion lets OBRM use each source for the role it performs best.

## Consequences

- Every stored row retains its selected provider.
- Metadata records contiguous provider segments.
- The Research Console displays provenance and freshness.
- A stale dataset is surfaced visibly rather than failing silently.
