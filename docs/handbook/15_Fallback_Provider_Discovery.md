# Research Handbook — Fallback Provider Discovery

## Purpose

The Evidence Registry defines what OBRM wants to know. Provider discovery asks
where that evidence might be obtained.

## Candidate is not validated

A provider appearing in the discovery registry means only that it may be worth
investigating. It does not mean:

- the data is free,
- the metric is available,
- the definition matches OBRM's evidence question,
- historical coverage is adequate,
- the licence permits reproducible use.

## Assessment criteria

Each provider/evidence pair is reviewed against six criteria:

1. Access method confirmed
2. Free access confirmed
3. Historical coverage confirmed
4. Metric definition confirmed
5. Reproducibility confirmed
6. Licensing confirmed

The assessment is visible and saved locally.

## Outcomes

- **Suitable:** every criterion passed.
- **Under review:** at least half passed, but blockers remain.
- **Unsuitable:** fewer than half passed.
- **Future:** deliberately deferred, such as self-computed Bitcoin Core data.

## Promotion boundary

A suitable provider does not automatically become part of the model. OBRM must
still implement an adapter, validate live data, normalize the schema, test the
research signal, and pass the formal promotion process.
