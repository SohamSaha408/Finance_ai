import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="Market Trends Data", page_icon="📊")

st.title("📊 Market Trends Data (Raw + Candlestick Chart)")
st.markdown("""
<p style='font-size: 1.1rem;'>Fetch and visualize historical stock/index data, including interactive candlestick charts.</p>
""", unsafe_allow_html=True)
st.info("Hint: For **Nifty 50**, use `^NSEI`. For **Reliance**, use `RELIANCE.NS`. For **Apple**, use `AAPL`.")

# --- User Input ---
market_ticker = st.text_input(
    "Enter Ticker (e.g., AAPL, ^NSEI, RELIANCE.NS)",
    value="^NSEI",
    key="market_trends_ticker_input"
).strip().upper()

today = datetime.now().date()
default_start = today - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=default_start, key="start_date")
with col2:
    end_date = st.date_input("End Date", value=today, key="end_date")

if st.button("Get Market Data"):
    if not market_ticker:
        st.warning("Ticker symbol cannot be empty.")
        st.stop()

    if start_date >= end_date:
        st.error("Start date must be earlier than end date.")
        st.stop()

    with st.spinner("Fetching data..."):
        try:
            data = yf.download(market_ticker, start=start_date, end=end_date)

            if not isinstance(data, pd.DataFrame) or data.empty:
                st.warning(f"No data found for '{market_ticker}' between {start_date} and {end_date}.")
                st.stop()

            # Convert and clean
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

            # --- Raw Data Display ---
            st.subheader(f"📄 Raw Data for {market_ticker}")
            st.dataframe(data.tail())

            # --- Key Metrics ---
            st.subheader("📌 Key Performance Metrics")
            first_open = data['Open'].iloc[0]
            last_close = data['Close'].iloc[-1]
            max_high = data['High'].max()
            min_low = data['Low'].min()
            total_volume = data['Volume'].sum()

            colm1, colm2, colm3, colm4, colm5 = st.columns(5)
            colm1.metric("Start Open", f"{first_open:.2f}" if not np.isnan(first_open) else "N/A")
            colm2.metric("End Close", f"{last_close:.2f}" if not np.isnan(last_close) else "N/A")
            colm3.metric("Max High", f"{max_high:.2f}" if not np.isnan(max_high) else "N/A")
            colm4.metric("Min Low", f"{min_low:.2f}" if not np.isnan(min_low) else "N/A")
            colm5.metric("Total Volume", f"{total_volume:,.0f}" if not np.isnan(total_volume) else "N/A")

            if first_open > 0:
                pct_change = ((last_close - first_open) / first_open) * 100
                st.metric("Price Change (%)", f"{pct_change:.2f}%", delta=f"{pct_change:.2f}%")
            else:
                st.info("Price change unavailable due to invalid starting price.")

            # --- Candlestick Chart ---
            st.subheader("📊 Candlestick Chart")
            fig = go.Figure(data=[
            go.Candlestick(
            x=data.index.tolist(),
            open=data['Open'].tolist(),
            high=data['High'].tolist(),
            low=data['Low'].tolist(),
            close=data['Close'].tolist(),
            name="Price"
            )
        ])


            fig.update_layout(
                title=f"Candlestick Chart for {market_ticker}",
                xaxis_title="Date",
                yaxis_title="Price",
                xaxis_rangeslider_visible=True,
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
