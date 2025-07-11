import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Market Trends Data", page_icon="📊")
st.title("📊 Market Trends Data (Raw Data Only)")

st.markdown(
    "<p style='font-size: 1.1rem;'>Fetch and view historical raw data for stock indices or individual company stocks.</p>",
    unsafe_allow_html=True,
)
st.info("Hint: For **Nifty 50**, use ticker `^NSEI`. For **Reliance Industries**, use `RELIANCE.NS`. For **Apple**, use `AAPL`.")

# --- User Inputs ---
market_ticker = st.text_input(
    "Enter Stock/Index Ticker Symbol (e.g., ^NSEI, RELIANCE.NS, AAPL):",
    value="^NSEI"
).strip().upper()

current_date = datetime.now().date()
default_start_date = current_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=default_start_date)
with col2:
    end_date = st.date_input("End Date", value=current_date)

if st.button("Get Market Data"):
    if not market_ticker:
        st.warning("Please enter a ticker symbol.")
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    try:
        df = yf.download(market_ticker, start=start_date, end=end_date)

        if df.empty:
            st.warning("No data found. Check the ticker or date range.")
            st.stop()

        for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        st.subheader(f"Raw Data for {market_ticker}")
        st.dataframe(df.head())

        open_val = df['Open'].iloc[0] if 'Open' in df.columns else None
        close_val = df['Close'].iloc[-1] if 'Close' in df.columns else None
        high_val = df['High'].max() if 'High' in df.columns else None
        low_val = df['Low'].min() if 'Low' in df.columns else None
        volume_val = df['Volume'].sum() if 'Volume' in df.columns else None

        metric_cols = st.columns(5)
        metric_cols[0].metric("Open", f"{open_val:.2f}" if open_val is not None else "N/A")
        metric_cols[1].metric("Close", f"{close_val:.2f}" if close_val is not None else "N/A")
        metric_cols[2].metric("High", f"{high_val:.2f}" if high_val is not None else "N/A")
        metric_cols[3].metric("Low", f"{low_val:.2f}" if low_val is not None else "N/A")
        metric_cols[4].metric("Volume", f"{volume_val:,.0f}" if volume_val is not None else "N/A")

        # Plot Candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(title=f"{market_ticker} Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
