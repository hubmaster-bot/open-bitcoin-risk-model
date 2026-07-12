# Developer Guide — Testing and Release Process

## Standard release sequence

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Release checklist

- Market data refresh succeeds
- Full test suite passes
- Dashboard launches
- New page or feature is manually inspected
- Documentation matches the code
- Changelog is updated
- ADR is added for major decisions
- Version number is updated
- Git commit and push complete

## Test categories

- Data validation
- Market data fusion
- Analytics
- Composite Risk
- Model Confidence
- Decision Engine
- Portfolio Layer
- Backtesting
- Walk-forward validation
- Presentation helpers
- Public registries and thresholds

## Rule

A failed test must be understood before it is changed.
