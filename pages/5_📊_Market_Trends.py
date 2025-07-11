import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Market Trends Data", page_icon="📊", layout="wide")

st.title("📊 Market Trends Data (with Candlestick Chart)")
st.markdown(
    """
    <p style='font-size: 1.1rem;'>Fetch and view historical stock/index data with metrics and candlestick chart.</p>
    """,
    unsafe_allow_html=True
)

st.info("Hint: For Nifty 50 use `^NSEI`, for Reliance use `RELIANCE.NS`, for Apple use `AAPL`.")

# User Inputs
ticker = st.text_input("Enter Ticker Symbol", value="^NSEI").strip().upper()

today = datetime.now().date()
one_year_ago = today - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=one_year_ago)
with col2:
    end_date = st.date_input("End Date", value=today)

# Fetch Data Button
if st.button("Get Market Data"):
    if not ticker:
        st.warning("Please enter a ticker symbol.")
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            df = yf.download(ticker, start=start_date, end=end_date)

            if df.empty or len(df) < 2:
                st.warning("No data found. Please check the ticker or date range.")
                st.stop()

            # Ensure numeric & fill missing
            for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            st.subheader(f"Raw Data for {ticker}")
            st.dataframe(df.tail())

            # Key Metrics
            st.subheader("📈 Key Metrics")
            open_val = df['Open'].iloc[0]
            close_val = df['Close'].iloc[-1]
            high_val = df['High'].max()
            low_val = df['Low'].min()
            volume_total = df['Volume'].sum()

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Start Open", f"{open_val:.2f}" if not np.isnan(open_val) else "N/A")
            col2.metric("End Close", f"{close_val:.2f}" if not np.isnan(close_val) else "N/A")
            col3.metric("Max High", f"{high_val:.2f}" if not np.isnan(high_val) else "N/A")
            col4.metric("Min Low", f"{low_val:.2f}" if not np.isnan(low_val) else "N/A")
            col5.metric("Total Volume", f"{volume_total:,.0f}")

            # Percentage Change
            if open_val and close_val and open_val != 0:
                change_pct = ((close_val - open_val) / open_val) * 100
                st.metric("Change (%)", f"{change_pct:.2f}%")
            else:
                st.info("Cannot calculate % change due to insufficient data.")

            # Candlestick Chart
            st.subheader("📊 Candlestick Chart")
            fig = go.Figure(data=[go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=ticker
            )])
            fig.update_layout(
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")
