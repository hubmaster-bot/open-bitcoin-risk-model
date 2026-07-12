# OBRM v0.4.2 Research Inspector hotfix

This hotfix makes the Research Inspector update continuously as the pointer moves anywhere across the chart plot area, rather than only when the pointer lands directly on a plotted line.

Copy `obrm/dashboard/inspector.py` over the existing file.

Then restart Streamlit:

```powershell
Ctrl + C
streamlit run app.py
```

No data refresh is required.
