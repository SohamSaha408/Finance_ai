from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="Market Trends Data", page_icon="📊", layout="wide")

st.title("📊 Market Trends Data (Raw Data + Candlestick Chart)")
st.markdown("""
<p style='font-size: 1.1rem;'>
Fetch and view historical raw data for stock indices or individual company stocks.
</p>""", unsafe_allow_html=True)
st.info("Hint: For **Nifty 50**, use ticker `^NSEI`. For **Reliance Industries**, use `RELIANCE.NS`. For **Apple**, use `AAPL`.")

# --- User Inputs ---
market_ticker = st.text_input("Enter Stock/Index Ticker Symbol (e.g., ^NSEI, RELIANCE.NS, AAPL):", value="^NSEI").strip().upper()
current_date = datetime.now().date()
default_start_date = current_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=default_start_date)
with col2:
    end_date = st.date_input("End Date", value=current_date)

# --- Fetch Data Button ---
if st.button("Get Market Data"):
    if not market_ticker:
        st.warning("Please enter a ticker symbol to fetch market data.")
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be before end date.")
        st.stop()

    with st.spinner(f"Fetching data for {market_ticker}..."):
        try:
            df = yf.download(market_ticker, start=start_date, end=end_date)

            if df.empty:
                st.warning("No data found. Check ticker or date range.")
                st.stop()

            # Clean Data
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Display Raw Data
            st.subheader(f"📄 Raw Data for {market_ticker}")
            st.dataframe(df.tail())

            # Key Metrics
            st.subheader("📊 Key Performance Metrics")
            open_val = df['Open'].iloc[0] if not df['Open'].empty else None
            close_val = df['Close'].iloc[-1] if not df['Close'].empty else None
            high_val = df['High'].max()
            low_val = df['Low'].min()
            volume = df['Volume'].sum()

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Open", f"{open_val:.2f}" if open_val else "N/A")
            col2.metric("Close", f"{close_val:.2f}" if close_val else "N/A")
            col3.metric("High", f"{high_val:.2f}")
            col4.metric("Low", f"{low_val:.2f}")
            col5.metric("Volume", f"{volume:,.0f}")

            # Price Change
            if open_val and close_val and open_val != 0:
                price_change_pct = ((close_val - open_val) / open_val) * 100
                st.metric("Price Change (%)", f"{price_change_pct:.2f}%")

            # Candlestick Chart
            st.subheader("🕯️ Candlestick Chart")
            fig = go.Figure(data=[
                go.Candlestick(
                    x=df.index,
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    increasing_line_color='green',
                    decreasing_line_color='red'
                )
            ])
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis_rangeslider_visible=False,
                template="plotly_dark",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
