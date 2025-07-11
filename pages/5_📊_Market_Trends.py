from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Market Trends Data", page_icon="📊")
st.title("📊 Market Trends Data (Raw Data + Candlestick Chart)")

st.markdown("""
<p style='font-size: 1.1rem;'>
    Fetch and view historical raw data and candlestick chart for stock indices or individual company stocks.
</p>
""", unsafe_allow_html=True)
st.info("Hint: For **Nifty 50**, use ticker `^NSEI`. For **Reliance Industries**, use `RELIANCE.NS`. For **Apple**, use `AAPL`.")

# --- User Inputs ---
market_ticker = st.text_input("Enter Stock/Index Ticker Symbol (e.g., ^NSEI, RELIANCE.NS, AAPL):",
                               value="^NSEI").strip().upper()

# Set default date range: 1 year prior to today
current_date = datetime.now().date()
default_start_date = current_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=default_start_date)
with col2:
    end_date = st.date_input("End Date", value=current_date)

# --- Fetch Data ---
if st.button("Get Market Data"):
    if not market_ticker:
        st.warning("Please enter a ticker symbol to fetch market data.")
        st.stop()

    if start_date >= end_date:
        st.error("Error: Start date must be before end date.")
        st.stop()

    with st.spinner(f"Fetching data for {market_ticker} from {start_date} to {end_date}..."):
        try:
            data = yf.download(market_ticker, start=start_date, end=end_date)

            if data.empty:
                st.warning(f"No data found for '{market_ticker}' between {start_date} and {end_date}.")
                st.stop()

            # Clean and fill NaN
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0)

            st.subheader(f"📄 Raw Data for {market_ticker}")
            st.dataframe(data.tail())

            # --- Candlestick Chart ---
            st.subheader("📈 Candlestick Chart")
            if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
                fig = go.Figure(data=[
                    go.Candlestick(
                        x=data.index,
                        open=data['Open'],
                        high=data['High'],
                        low=data['Low'],
                        close=data['Close'],
                        name="Candlestick"
                    )
                ])
                fig.update_layout(
                    title=f"Candlestick Chart for {market_ticker}",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    xaxis_rangeslider_visible=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Required columns for candlestick chart are missing.")

            # --- Key Metrics ---
            st.subheader("📊 Key Metrics")
            first_open = data['Open'].iloc[0]
            last_close = data['Close'].iloc[-1]
            max_high = data['High'].max()
            min_low = data['Low'].min()
            total_volume = data['Volume'].sum()

            fo_str = f"{first_open:.2f}" if not np.isnan(first_open) else "N/A"
            lc_str = f"{last_close:.2f}" if not np.isnan(last_close) else "N/A"
            mh_str = f"{max_high:.2f}" if not np.isnan(max_high) else "N/A"
            ml_str = f"{min_low:.2f}" if not np.isnan(min_low) else "N/A"
            tv_str = f"{total_volume:,.0f}" if not np.isnan(total_volume) else "N/A"

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Start Open", fo_str)
            col2.metric("End Close", lc_str)
            col3.metric("Max High", mh_str)
            col4.metric("Min Low", ml_str)
            col5.metric("Total Volume", tv_str)

            if first_open != 0 and not np.isnan(first_open) and not np.isnan(last_close):
                change_pct = ((last_close - first_open) / first_open) * 100
                st.metric("Price Change (%)", f"{change_pct:.2f}%", delta=f"{change_pct:.2f}%")
            else:
                st.info("Cannot calculate percentage change.")

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

