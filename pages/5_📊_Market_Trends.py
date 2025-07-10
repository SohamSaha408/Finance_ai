import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np # Make sure numpy is imported for np.isnan

st.title("📊 Market Trends Data (Raw Data Only)")
st.markdown("<p style='font-size: 1.1rem;'>View raw historical data for Nifty 50 or other stock/index symbols.</p>", unsafe_allow_html=True)
st.info("Hint: For **Nifty 50**, use ticker `^NSEI`. For **Reliance Industries**, use `RELIANCE.NS`. For **Apple**, use `AAPL`.")

market_ticker = st.text_input(
    "Enter Stock/Index Ticker Symbol (e.g., ^NSEI, RELIANCE.NS):",
    value="^NSEI", # Default to Nifty 50
    key="mt_market_ticker_input"
).strip().upper()

# Set default start date to 1 year ago and end date to today
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date, key="mt_chart_start_date")
with col2:
    chart_end_date = st.date_input("End Date", value=end_date, key="mt_chart_end_date")

if st.button("Get Market Data", key="mt_get_market_data_btn"):
    if market_ticker:
        with st.spinner(f"Fetching historical data for {market_ticker}..."):
            try:
                data = yf.download(market_ticker, start=chart_start_date, end=chart_end_date)

                # --- CRITICAL FIX: Handle empty data immediately ---
                if data.empty:
                    st.warning(f"No historical data found for '{market_ticker}' in the specified date range ({chart_start_date} to {chart_end_date}). This could be due to an incorrect ticker, an unsupported date range, or no trading activity.")
                    if 'ai_summary_data' not in st.session_state:
                        st.session_state['ai_summary_data'] = {}
                    st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                        "ticker": market_ticker,
                        "date_range": f"{chart_start_date} to {chart_end_date}",
                        "data_summary": "No data found."
                    }
                    return # Exit the function/block if no data is found, preventing subsequent errors

                # ONLY proceed with data processing if data is NOT empty
                st.write("--- Raw Data Fetched (Head) ---")
                for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                    if col in data.columns:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
                        data[col] = data[col].fillna(0)

                st.dataframe(data.head())
                st.write("--- Raw Data Fetched (Tail) ---")
                st.dataframe(data.tail())
                st.write("-----------------------------")

                # These variables will now be safe to access as 'data' is not empty
                first_open = data['Open'].iloc[0] if not data['Open'].empty else None
                last_close = data['Close'].iloc[-1] if not data['Close'].empty else None
                max_high = data['High'].max() if not data['High'].empty else None
                min_low = data['Low'].min() if not data['Low'].empty else None

                summary_parts = [f"Fetched {len(data)} data points."]
                # Ensure values are not None/NaN before formatting with :.2f
                summary_parts.append(f"Start Open: {first_open:.2f}" if first_open is not None and not np.isnan(first_open) else "Start Open: N/A")
                summary_parts.append(f"End Close: {last_close:.2f}" if last_close is not None and not np.isnan(last_close) else "End Close: N/A")
                summary_parts.append(f"Max High: {max_high:.2f}" if max_high is not None and not np.isnan(max_high) else "Max High: N/A")
                summary_parts.append(f"Min Low: {min_low:.2f}" if min_low is not None and not np.isnan(min_low) else "Min Low: N/A")

                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                    "ticker": market_ticker,
                    "date_range": f"{chart_start_date} to {chart_end_date}",
                    "data_summary": ", ".join(summary_parts)
                }

            except Exception as e:
                st.error(f"An error occurred while fetching market data for {market_ticker}: {e}. Please ensure the ticker is correct and try again with a valid date range.")
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                    "ticker": market_ticker,
                    "date_range": f"{chart_start_date} to {chart_end_date}",
                    "data_summary": f"Error during fetch: {e}"
                }
    else:
        st.warning("Please enter a ticker symbol to fetch market trends.")
st.markdown("---")
