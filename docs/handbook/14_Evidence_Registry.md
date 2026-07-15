# Research Handbook — Evidence Registry

## Purpose

The Evidence Registry describes what OBRM wants to know before deciding where
the data should come from.

This separates four concepts:

1. **Evidence** — the economic or market question.
2. **Provider mapping** — a provider-specific metric that may answer it.
3. **Research signal** — a normalized calculation derived from validated data.
4. **Market Dimension** — promoted evidence that has passed formal validation.

## Initial evidence roadmap

| Evidence | Domain | Status |
|---|---|---|
| Realized Valuation | On-Chain | Validated |
| Network Strength | On-Chain | Validated |
| Holder Behaviour | On-Chain | Missing |
| Realized Capital Flow | On-Chain | Missing |
| Market Liquidity | Liquidity | Planned |
| Macro Regime | Macro | Planned |
| Derivatives Positioning | Market Structure | Planned |
| Market Sentiment | Sentiment | Planned |

## Coverage

Overall coverage is the number of validated evidence items divided by the total
registry size. This is a roadmap measure, not Model Confidence and not a
probability that the model is correct.

Required On-Chain coverage considers only the evidence declared necessary for
the candidate On-Chain Market Dimension. At v0.10.0, two of four required
categories are validated.

## Provider mappings

A provider mapping records:

- provider name,
- provider metric identifier,
- access and validation status,
- metric definition,
- provenance notes,
- and preference priority.

A mapping may be validated, available, forbidden, a candidate, or a future
self-computed source.

## Evidence-first workflow

1. Define the evidence and its purpose.
2. Register potential provider mappings.
3. Verify access, coverage, definition, and data quality.
4. Build a no-look-ahead research signal.
5. Test forward-return separation and redundancy.
6. Complete a formal promotion review.
7. Change the live model only in a separate implementation release.

## Design principle

OBRM uses the best validated evidence available. It does not define the model by
one vendor's catalogue.
