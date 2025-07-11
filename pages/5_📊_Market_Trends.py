import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np # Used for checking Not-a-Number (NaN) values

st.set_page_config(page_title="Market Trends Data", page_icon="📊")

st.title("📊 Market Trends Data (Raw Data Only)")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Fetch and view historical raw data for stock indices or individual company stocks.
    </p>
    """, unsafe_allow_html=True)
st.info("Hint: For **Nifty 50**, use ticker `^NSEI`. For **Reliance Industries**, use `RELIANCE.NS`. For **Apple**, use `AAPL`.")

# --- User Inputs ---
market_ticker = st.text_input(
    "Enter Stock/Index Ticker Symbol (e.g., ^NSEI, RELIANCE.NS, AAPL):",
    value="^NSEI", # Default to Nifty 50
    key="market_trends_ticker_input"
).strip().upper() # Clean input: remove whitespace and convert to uppercase

# Set default date range: 1 year prior to today
current_date = datetime.now().date()
default_start_date = current_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=default_start_date, key="market_trends_start_date")
with col2:
    end_date = st.date_input("End Date", value=current_date, key="market_trends_end_date")

# --- Fetch Data Button ---
if st.button("Get Market Data", key="get_market_data_button"):
    if not market_ticker:
        st.warning("Please enter a ticker symbol to fetch market data.")
        st.session_state['ai_summary_data'] = {'Market Trend Visualization': {'status': 'No ticker entered'}}
        st.stop() # Stop execution if no ticker

    if start_date >= end_date:
        st.error("Error: Start date must be before end date. Please adjust the dates.")
        st.session_state['ai_summary_data'] = {'Market Trend Visualization': {'status': 'Invalid date range'}}
        st.stop() # Stop execution for invalid date range

    # --- Data Fetching and Display Logic ---
    with st.spinner(f"Fetching historical data for {market_ticker} from {start_date} to {end_date}..."):
        try:
            # Download data using yfinance
            data = yf.download(market_ticker, start=start_date, end=end_date)

            # Check if the DataFrame is empty (no data found)
            if data.empty:
                st.warning(
                    f"No historical data found for '{market_ticker}' in the specified date range "
                    f"({start_date} to {end_date}). This could be due to an incorrect ticker, "
                    "an unsupported date range (e.g., future dates or very new listings), or no trading activity "
                    "(e.g., holidays, weekends)."
                )
                # Update AI summary for no data scenario
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                    "ticker": market_ticker,
                    "date_range": f"{start_date} to {end_date}",
                    "data_summary": "No data found.",
                    "status": "Success (No data)"
                }
                st.stop() # Stop further execution if no data is found

            # Clean and prepare data for display and calculations
            for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce') # Convert to numeric, errors become NaN
                    data[col] = data[col].fillna(0) # Fill NaN values with 0 for consistent calculations

            st.subheader(f"Raw Data for {market_ticker}")
            st.write("--- Head ---")
            st.dataframe(data.head())
            st.write("--- Tail ---")
            st.dataframe(data.tail())
            st.write("-----------------------------")

            # --- Display Key Metrics ---
            st.subheader("Key Performance Metrics")
            if not data.empty:
                first_open = data['Open'].iloc[0]
                last_close = data['Close'].iloc[-1]
                max_high = data['High'].max()
                min_low = data['Low'].min()
                total_volume = data['Volume'].sum()

                # Robust formatting to handle potential NaN values after fillna(0)
                # np.isnan is crucial here as fillna(0) might still leave NaNs if original data was not numeric
                fo_str = f"{first_open:.2f}" if first_open is not None and not np.isnan(first_open) else "N/A"
                lc_str = f"{last_close:.2f}" if last_close is not None and not np.isnan(last_close) else "N/A"
                mh_str = f"{max_high:.2f}" if max_high is not None and not np.isnan(max_high) else "N/A"
                ml_str = f"{min_low:.2f}" if min_low is not None and not np.isnan(min_low) else "N/A"
                tv_str = f"{total_volume:,.0f}" if total_volume is not None and not np.isnan(total_volume) else "N/A"


                # Display metrics in columns
                metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
                with metric_col1:
                    st.metric("Start Open", fo_str)
                with metric_col2:
                    st.metric("End Close", lc_str)
                with metric_col3:
                    st.metric("Max High", mh_str)
                with metric_col4:
                    st.metric("Min Low", ml_str)
                with metric_col5:
                    st.metric("Total Volume", tv_str)

                # Optional: Simple price change calculation
                if first_open and last_close and not np.isnan(first_open) and not np.isnan(last_close) and first_open != 0:
                    price_change_pct = ((last_close - first_open) / first_open) * 100
                    st.metric("Price Change (%)", f"{price_change_pct:.2f}%", delta=f"{price_change_pct:.2f}%")
                else:
                    st.info("Cannot calculate percentage change (insufficient data or start price is zero).")


                # --- Prepare data for AI Summary ---
                summary_parts = [
                    f"Fetched {len(data)} data points for {market_ticker} from {start_date} to {end_date}.",
                    f"Start Open: {fo_str}",
                    f"End Close: {lc_str}",
                    f"Max High: {mh_str}",
                    f"Min Low: {ml_str}",
                    f"Total Volume: {tv_str}"
                ]
                if first_open and last_close and not np.isnan(first_open) and not np.isnan(last_close) and first_open != 0:
                     summary_parts.append(f"Percentage Change: {price_change_pct:.2f}%")

                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                    "ticker": market_ticker,
                    "date_range": f"{start_date} to {end_date}",
                    "data_summary": ", ".join(summary_parts),
                    "status": "Success"
                }

            else:
                st.warning("No data available to display metrics.")
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                    "ticker": market_ticker,
                    "date_range": f"{start_date} to {end_date}",
                    "data_summary": "Dataframe became empty after processing (e.g., all NaNs).",
                    "status": "Success (Empty after process)"
                }


        except Exception as e:
            # Catch any unexpected errors during the process
            st.error(f"An unexpected error occurred while fetching or processing market data for {market_ticker}: {e}. Please check the ticker symbol, date range, or your internet connection.")
            # Update AI summary for error scenario
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                "ticker": market_ticker,
                "date_range": f"{start_date} to {end_date}",
                "data_summary": f"Error during fetch/process: {e}",
                "status": "Error"
            }
    st.markdown("---")
else:
    # Initial load message or instruction
    st.info("Enter a stock or index ticker symbol and select a date range, then click 'Get Market Data' to view historical information.")

st.markdown("---") # Visual separator at the bottom of the page
