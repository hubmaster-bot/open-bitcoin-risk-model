"""Stable click-to-inspect Plotly chart for OBRM."""

from __future__ import annotations

import html
import json
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

FAIR_VALUE_COLOUR = "#2ECC71"
PRICE_COLOUR = "#5DADE2"
RISK_COLOUR = "#FF9AA2"
CROSSHAIR_COLOUR = "#C9D1D9"
CONFIDENCE_HIGH_COLOUR = "#2ECC71"
CONFIDENCE_MEDIUM_COLOUR = "#F4B942"
CONFIDENCE_LOW_COLOUR = "#E57373"


def _confidence_class(value: float) -> str:
    """Return the display class for a confidence percentage."""
    if value >= 0.80:
        return "confidence-high"
    if value >= 0.60:
        return "confidence-medium"
    return "confidence-low"


def _reasoning(
    premium_pct: float,
    risk: float,
    confidence: float,
) -> list[str]:
    """Create concise, transparent model notes for one observation."""
    notes: list[str] = []

    if premium_pct <= -30:
        notes.append("Price is materially below the current fair-value estimate.")
    elif premium_pct < 0:
        notes.append("Price is below the current fair-value estimate.")
    elif premium_pct < 30:
        notes.append("Price is moderately above the current fair-value estimate.")
    else:
        notes.append("Price is materially above the current fair-value estimate.")

    if risk <= 0.20:
        notes.append("Price-position risk is in the Deep Value range.")
    elif risk <= 0.40:
        notes.append("Price-position risk is in the Accumulation range.")
    elif risk <= 0.60:
        notes.append("Price-position risk is in the Neutral range.")
    elif risk <= 0.80:
        notes.append("Price-position risk is in the Caution range.")
    else:
        notes.append("Price-position risk is in the Distribution range.")

    if confidence >= 0.80:
        notes.append("Regression fit and sample maturity are strong.")
    elif confidence >= 0.60:
        notes.append("Regression fit and sample maturity are moderate.")
    else:
        notes.append("Regression fit or sample maturity is limited.")

    notes.append(
        "Momentum, volatility, on-chain, macro, and full confidence inputs are not included yet."
    )
    return notes


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Return JSON-safe records for the browser-side inspector."""
    rows: list[dict[str, Any]] = []

    for row in df.itertuples(index=False):
        confidence = float(row.preliminary_confidence)
        premium_pct = float(row.premium_pct)
        risk = float(row.price_position_risk)

        rows.append(
            {
                "date": pd.Timestamp(row.date).strftime("%d-%b-%Y"),
                "date_iso": pd.Timestamp(row.date).strftime("%Y-%m-%d"),
                "price": float(row.price_usd),
                "fair_value": float(row.fair_value_usd),
                "premium_pct": premium_pct,
                "risk": risk,
                "confidence": confidence,
                "confidence_class": _confidence_class(confidence),
                "phase": str(row.market_phase),
                "dca_multiplier": float(row.dca_multiplier),
                "dca_label": str(row.dca_label),
                "provider": str(row.provider),
                "notes": _reasoning(premium_pct, risk, confidence),
            }
        )

    return rows


def build_chart_figure(df: pd.DataFrame) -> go.Figure:
    """Build the combined price, fair-value, and risk chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["price_usd"],
            mode="lines",
            name="BTC Price",
            line={"color": PRICE_COLOUR, "width": 1.6},
            hoverinfo="skip",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["fair_value_usd"],
            mode="lines",
            name="Log Regression Fair Value",
            line={"color": FAIR_VALUE_COLOUR, "width": 1.6},
            hoverinfo="skip",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["price_position_risk"],
            mode="lines",
            name="Price Position Risk",
            line={"color": RISK_COLOUR, "width": 1.5},
            hoverinfo="skip",
        ),
        secondary_y=True,
    )

    fig.update_yaxes(
        title_text="BTC Price (USD, log scale)",
        type="log",
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Risk",
        range=[0, 1],
        secondary_y=True,
    )

    fig.update_layout(
        title={
            "text": "Bitcoin Price, Fair Value, and Price Position Risk",
            "x": 0.0,
            "xanchor": "left",
            "y": 0.985,
            "yanchor": "top",
        },
        xaxis_title="Date",
        hovermode=False,
        clickmode="event",
        height=880,
        margin={"l": 70, "r": 55, "t": 145, "b": 60},
        legend={
            "orientation": "h",
            "x": 0.0,
            "xanchor": "left",
            "y": 0.925,
            "yanchor": "bottom",
        },
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
    )
    return fig


def build_chart_with_inspector_html(df: pd.DataFrame) -> str:
    """Return self-contained chart HTML with click-to-inspect behaviour."""
    plotted = df.dropna(
        subset=[
            "fair_value_usd",
            "price_position_risk",
            "preliminary_confidence",
            "dca_multiplier",
        ]
    ).copy()

    figure_json = build_chart_figure(plotted).to_json()
    records = _records(plotted)
    records_json = json.dumps(records)
    latest = records[-1]

    def currency(value: float) -> str:
        return f"${value:,.0f}"

    notes_html = "".join(
        f"<li>{html.escape(note)}</li>" for note in latest["notes"]
    )

    initial_html = f"""
      <div class="inspector-date">{html.escape(latest['date'])}</div>
      <div class="metric-row"><span><i>₿</i> BTC Price</span><strong>{currency(latest['price'])}</strong></div>
      <div class="metric-row"><span><i>≈</i> Fair Value</span><strong class="green">{currency(latest['fair_value'])}</strong></div>
      <div class="metric-row"><span><i>Δ</i> Premium / Discount</span><strong>{latest['premium_pct']:+.1f}%</strong></div>
      <div class="metric-row"><span><i>◉</i> Price Position Risk</span><strong class="risk">{latest['risk']:.2f}</strong></div>
      <div class="metric-row"><span><i>%</i> Preliminary Confidence</span><strong class="{latest['confidence_class']}">{latest['confidence']:.0%}</strong></div>
      <div class="metric-row"><span><i>◇</i> Market Phase</span><strong>{html.escape(latest['phase'])}</strong></div>
      <div class="metric-row"><span><i>↕</i> Suggested DCA</span><strong>{latest['dca_multiplier']:.2f}× normal</strong></div>
      <div class="metric-row"><span><i>—</i> DCA Band</span><strong>{html.escape(latest['dca_label'])}</strong></div>
      <div class="metric-row"><span><i>ⓘ</i> Source</span><strong>{html.escape(latest['provider'])}</strong></div>
      <section class="model-notes">
        <h4>Model Notes</h4>
        <ul>{notes_html}</ul>
      </section>
    """

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
html, body {{
  margin: 0;
  background: #0E1117;
  color: #FAFAFA;
  font-family: Arial, sans-serif;
}}
.layout {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) 400px;
  gap: 18px;
  align-items: stretch;
}}
#chart {{
  min-width: 0;
  height: 880px;
}}
.inspector {{
  border: 1px solid #30363D;
  border-radius: 10px;
  background: #111821;
  padding: 20px;
  height: 844px;
  overflow-y: auto;
  box-sizing: border-box;
}}
.inspector h3 {{
  margin: 0 0 18px;
  color: {FAIR_VALUE_COLOUR};
  font-size: 20px;
}}
.inspector-date {{
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 18px;
}}
.metric-row {{
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 9px 0;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  font-size: 14px;
}}
.metric-row span {{
  color: #B8C0CC;
}}
.metric-row span i {{
  display: inline-block;
  width: 18px;
  color: #7D8590;
  font-style: normal;
  text-align: center;
  margin-right: 6px;
}}
.metric-row strong {{
  text-align: right;
  font-weight: 650;
}}
.green {{ color: {FAIR_VALUE_COLOUR}; }}
.risk {{ color: {RISK_COLOUR}; }}
.confidence-high {{ color: {CONFIDENCE_HIGH_COLOUR}; }}
.confidence-medium {{ color: {CONFIDENCE_MEDIUM_COLOUR}; }}
.confidence-low {{ color: {CONFIDENCE_LOW_COLOUR}; }}
.model-notes {{
  margin-top: 20px;
  padding: 14px 15px;
  border: 1px solid #30363D;
  border-radius: 8px;
  background: #0E151D;
}}
.model-notes h4 {{
  margin: 0 0 10px;
  color: #DDE4EC;
  font-size: 14px;
}}
.model-notes ul {{
  margin: 0;
  padding-left: 18px;
  color: #B8C0CC;
  font-size: 13px;
  line-height: 1.55;
}}
.hint {{
  margin-top: 16px;
  color: #8B949E;
  font-size: 12px;
  line-height: 1.5;
}}
@media (max-width: 1120px) {{
  .layout {{
    grid-template-columns: 1fr;
  }}
  .inspector {{
    height: auto;
  }}
}}
</style>
</head>
<body>
<div class="layout">
  <div id="chart"></div>
  <aside class="inspector">
    <h3>Research Inspector</h3>
    <div id="inspector-content">{initial_html}</div>
    <div class="hint">
      Click anywhere inside the plotting area to inspect and lock a historical date.
    </div>
  </aside>
</div>

<script>
const figure = {figure_json};
const records = {records_json};
const chart = document.getElementById("chart");
const inspector = document.getElementById("inspector-content");

const recordTimes = records.map(row => new Date(row.date_iso + "T00:00:00Z").getTime());

const money = value => new Intl.NumberFormat("en-US", {{
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
}}).format(value);

const percent = value =>
  `${{value >= 0 ? "+" : ""}}${{value.toFixed(1)}}%`;

const escapeHtml = value =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const nearestRecord = targetTime => {{
  let low = 0;
  let high = recordTimes.length - 1;

  while (low < high) {{
    const mid = Math.floor((low + high) / 2);
    if (recordTimes[mid] < targetTime) low = mid + 1;
    else high = mid;
  }}

  const right = low;
  const left = Math.max(0, right - 1);

  return Math.abs(recordTimes[left] - targetTime)
    <= Math.abs(recordTimes[right] - targetTime)
    ? records[left]
    : records[right];
}};

const renderInspector = row => {{
  const notes = row.notes
    .map(note => `<li>${{escapeHtml(note)}}</li>`)
    .join("");

  inspector.innerHTML = `
    <div class="inspector-date">${{row.date}}</div>
    <div class="metric-row"><span><i>₿</i> BTC Price</span><strong>${{money(row.price)}}</strong></div>
    <div class="metric-row"><span><i>≈</i> Fair Value</span><strong class="green">${{money(row.fair_value)}}</strong></div>
    <div class="metric-row"><span><i>Δ</i> Premium / Discount</span><strong>${{percent(row.premium_pct)}}</strong></div>
    <div class="metric-row"><span><i>◉</i> Price Position Risk</span><strong class="risk">${{row.risk.toFixed(2)}}</strong></div>
    <div class="metric-row"><span><i>%</i> Preliminary Confidence</span><strong class="${{row.confidence_class}}">${{Math.round(row.confidence * 100)}}%</strong></div>
    <div class="metric-row"><span><i>◇</i> Market Phase</span><strong>${{escapeHtml(row.phase)}}</strong></div>
    <div class="metric-row"><span><i>↕</i> Suggested DCA</span><strong>${{row.dca_multiplier.toFixed(2)}}× normal</strong></div>
    <div class="metric-row"><span><i>—</i> DCA Band</span><strong>${{escapeHtml(row.dca_label)}}</strong></div>
    <div class="metric-row"><span><i>ⓘ</i> Source</span><strong>${{escapeHtml(row.provider)}}</strong></div>
    <section class="model-notes">
      <h4>Model Notes</h4>
      <ul>${{notes}}</ul>
    </section>
  `;
}};

const lockCrosshair = row => {{
  Plotly.relayout(chart, {{
    shapes: [{{
      type: "line",
      xref: "x",
      yref: "paper",
      x0: row.date_iso,
      x1: row.date_iso,
      y0: 0,
      y1: 1,
      line: {{
        color: "{CROSSHAIR_COLOUR}",
        width: 1,
        dash: "dot"
      }}
    }}]
  }});
}};

const selectByTime = targetTime => {{
  const row = nearestRecord(targetTime);
  renderInspector(row);
  lockCrosshair(row);
}};

Plotly.newPlot(chart, figure.data, figure.layout, {{
  responsive: true,
  displaylogo: false,
  scrollZoom: true
}}).then(() => {{
  lockCrosshair(records[records.length - 1]);

  const plotArea = chart.querySelector(".nsewdrag");

  if (plotArea) {{
    plotArea.addEventListener("click", event => {{
      const bounds = plotArea.getBoundingClientRect();
      const pixelX = event.clientX - bounds.left;

      if (pixelX < 0 || pixelX > bounds.width) return;

      const xValue = chart._fullLayout.xaxis.p2d(pixelX);
      const targetTime = new Date(xValue).getTime();

      if (!Number.isNaN(targetTime)) {{
        selectByTime(targetTime);
      }}
    }});
  }}

  chart.on("plotly_click", event => {{
    if (!event.points || !event.points.length) return;
    const targetTime = new Date(event.points[0].x).getTime();

    if (!Number.isNaN(targetTime)) {{
      selectByTime(targetTime);
    }}
  }});
}});
</script>
</body>
</html>
"""


def inspector_height() -> int:
    """Return the Streamlit component height."""
    return 900
