# Research Handbook — Holder Behaviour Research

## Question

Are older coins remaining dormant, or are experienced holders increasingly
spending and distributing supply?

## Portable evidence

OBRM does not assume that similarly named provider metrics are equivalent.
Version 0.10.2 therefore accepts a reviewed daily dataset only when the user
records:

- provider or dataset owner,
- provider metric name,
- exact definition,
- licence or usage note,
- source URL where available,
- metric direction.

## Supported metric kinds

### Dormancy and coin days destroyed

Higher values generally indicate that older coins are moving. OBRM maps higher
expanding percentiles to a higher distribution-risk research score.

### Long-term-holder or dormant-supply percentage

Higher values generally indicate stronger holder conviction. OBRM inverts the
expanding percentile so stronger conviction produces a lower research score.

## No-look-ahead calculation

Each daily value is ranked only against observations available on or before that
date. A 30-day average reduces noise.

## Research status

The logical evidence moves from Missing to Research, not Validated. A dataset
still requires source review, historical validation, redundancy testing, and a
promotion decision before it can influence the model.
