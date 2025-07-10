# In pages/5_📊_Market_Trends.py

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np # Ensure numpy is imported for np.isnan

# ... (rest of your page setup code) ...

if st.button("Get Market Data", key="mt_get_market_data_btn"):
    if market_ticker:
        with st.spinner(f"Fetching historical data for {market_ticker}..."):
            try:
                data = yf.download(market_ticker, start=chart_start_date, end=chart_end_date)

                # --- APPLY THIS FIX ---
                if data.empty:
                    st.warning(f"No historical data found for '{market_ticker}' in the specified date range ({chart_start_date} to {chart_end_date}). This could be due to an incorrect ticker, an unsupported date range, or no trading activity.")
                    # Update AI summary data for no results
                    if 'ai_summary_data' not in st.session_state:
                        st.session_state['ai_summary_data'] = {}
                    st.session_state['ai_summary_data']['Market Trend Visualization'] = {
                        "ticker": market_ticker,
                        "date_range": f"{chart_start_date} to {chart_end_date}",
                        "data_summary": "No data found."
                    }
                    return # <--- This is the crucial line: Exit if no data is found

                # --- ONLY execute the following code if 'data' is NOT empty ---
                st.write("--- Raw Data Fetched (Head) ---")
                for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
                    if col in data.columns:
                        data[col] = pd.to_numeric(data[col], errors='coerce')
                        data[col] = data[col].fillna(0)

                st.dataframe(data.head())
                st.write("--- Raw Data Fetched (Tail) ---")
                st.dataframe(data.tail())
                st.write("-----------------------------")

                first_open = data['Open'].iloc[0] if not data['Open'].empty else None
                last_close = data['Close'].iloc[-1] if not data['Close'].empty else None
                max_high = data['High'].max() if not data['High'].empty else None
                min_low = data['Low'].min() if not data['Low'].empty else None

                summary_parts = [f"Fetched {len(data)} data points."]
                # These conditional formats prevent errors if values are None or NaN
                summary_parts.append(f"Start Open: {first_open:.2f}" if first_open is not None and not np.isnan(first_open) else "Start Open: N/A")
                summary_parts.append(f"End Close: {last_close:.2f}" if last_close is not None and not np.isnan(last_close) else "End Close: N/A")
                summary_parts.append(f"Max High: {max_high:.2f}" if max_high is not None and not np.isnan(max_high) else "Max High: N/A")
                summary_parts.append(f"Min Low: {min_low:.2f}" if min_low is not None and not np.isnan(min_low) else "Min Low: N/A")

                # ... (rest of your AI summary data capture for success) ...

            except Exception as e:
                st.error(f"An error occurred while fetching market data for {market_ticker}: {e}. Please ensure the ticker is correct and try again with a valid date range.")
                # ... (rest of your AI summary data capture for error) ...
    else:
        st.warning("Please enter a ticker symbol to fetch market trends.")
st.markdown("---")
