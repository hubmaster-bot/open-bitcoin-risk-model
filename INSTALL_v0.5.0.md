# OBRM v0.5.0 — Multi-Factor Risk Engine Alpha

Copy the release contents over the repository root.

## Run order

```powershell
python -m obrm
python -m pytest
streamlit run app.py
```

## Verify

- Version displays as `0.5.0`.
- Tests pass.
- The chart uses native Plotly again.
- The chart shows BTC price, fair value, and Composite OBRM Risk.
- Dashboard shows valuation, momentum, volatility, and component agreement.
- Confidence v1 appears.
- Decision Engine preview appears.
- High-risk historical dates can show preview DCA-out guidance.
- Research Console shows component weights and latest values.

## Commit

```powershell
git add .
git commit -m "Release v0.5.0 - Add Multi-Factor Risk Engine"
git push origin main
```
