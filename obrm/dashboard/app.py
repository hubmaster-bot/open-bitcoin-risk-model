"""Streamlit dashboard for OBRM."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from obrm.core.config import load_config
from obrm.core.version import APP_NAME, APP_VERSION
from obrm.data.engine import MarketDataEngine


def format_date(value: object) -> str:
    """Format dates as DD-Mon-YYYY."""
    return pd.Timestamp(value).strftime("%d-%b-%Y")


@st.cache_data
def load_price_data() -> pd.DataFrame:
    """Load BTC price history through the Market Data Engine."""
    return MarketDataEngine().get_btc_price_history()


def build_price_chart(df: pd.DataFrame) -> go.Figure:
    """Build the first OBRM logarithmic BTC price chart."""
    custom_dates = pd.to_datetime(df["date"]).dt.strftime("%d-%b-%Y")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["price_usd"],
            mode="lines",
            name="BTC Price",
            customdata=custom_dates,
            hovertemplate=(
                "<b>%{customdata}</b><br>"
                "BTC Price: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Bitcoin Price History",
        xaxis_title="Date",
        yaxis_title="BTC Price (USD, log scale)",
        yaxis_type="log",
        hovermode="x unified",
        height=760,
    )
    return fig


def main() -> None:
    """Render the OBRM dashboard."""
    st.set_page_config(
        page_title="OBRM Dashboard",
        page_icon="📈",
        layout="wide",
    )

    config = load_config()
    st.title(APP_NAME)
    st.caption(f"Version {APP_VERSION}")

    df = load_price_data()
    latest = df.iloc[-1]
    first = df.iloc[0]

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest BTC Price", f"${latest['price_usd']:,.0f}")
    col2.metric("Latest Date", format_date(latest["date"]))
    col3.metric("Provider", str(latest["provider"]))

    st.plotly_chart(build_price_chart(df), use_container_width=True)

    st.caption(
        f"Data begins: {format_date(first['date'])} · "
        f"Rows: {len(df):,} · "
        f"Configured primary provider: {config.primary_provider}"
    )


if __name__ == "__main__":
    main()
