import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈")

st.title("📈 Nifty 50 Candlestick Chart")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Visualize the historical price movements of the Nifty 50 index with an interactive candlestick chart.
    </p>
    """, unsafe_allow_html=True)

# --- Define the Nifty 50 Ticker ---
NIFTY_TICKER = "^NSEI" # Standard ticker for Nifty 50

# --- Date Range Selection ---
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365) # Default to 1 year ago

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date, key="nifty_chart_start_date")
with col2:
    chart_end_date = st.date_input("End Date", value=end_date, key="nifty_chart_end_date")

# --- Fetch and Display Chart Button ---
if st.button("Get Nifty 50 Chart", key="get_nifty_chart_btn"):
    if chart_start_date >= chart_end_date:
        st.error("Error: Start date must be before end date. Please adjust the dates.")
        st.stop()

    with st.spinner(f"Fetching historical data for Nifty 50 ({NIFTY_TICKER})..."):
        try:
            # Fetch data using yfinance
            data = yf.download(NIFTY_TICKER, start=chart_start_date, end=chart_end_date)

            # --- CRITICAL VALIDATION 1: Check if DataFrame is empty ---
            if data.empty:
                st.warning(f"No historical data found for Nifty 50 in the specified date range ({chart_start_date} to {chart_end_date}). This could be due to no trading activity on selected dates (e.g., holidays).")
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                    "ticker": NIFTY_TICKER,
                    "date_range": f"{chart_start_date} to {chart_end_date}",
                    "chart_status": "No data found."
                }
                st.stop() # Stop further execution if no data

            # Ensure numeric columns are clean (useful for robustness)
            # This step helps ensure Plotly receives valid numeric data
            required_cols = ['Open', 'High', 'Low', 'Close']
            for col in required_cols + ['Adj Close', 'Volume']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
                    # Fill NaNs specifically for plotting to avoid errors.
                    # Consider using forward/backward fill for actual analysis, but 0 is fine for chart display if missing.
                    data[col] = data[col].fillna(0) # Fill any NaNs with 0

            # --- CRITICAL VALIDATION 2: Check if required columns have valid data ---
            # After converting to numeric and filling NaNs, ensure the columns aren't all zeros/N/A
            if not all(col in data.columns and not data[col].isnull().all() for col in required_cols):
                 st.warning(f"Insufficient valid data in required columns (Open, High, Low, Close) for {NIFTY_TICKER} to plot a chart. This might happen if all values are zero or missing after data cleaning.")
                 if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                 st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                    "ticker": NIFTY_TICKER,
                    "date_range": f"{chart_start_date} to {chart_end_date}",
                    "chart_status": "Insufficient valid data for plotting."
                 }
                 st.stop() # Stop further execution if data is invalid

            # --- Candlestick Chart Generation ---
            st.subheader(f"Nifty 50 Candlestick Chart ({chart_start_date} to {chart_end_date})")

            fig = go.Figure(data=[go.Candlestick(x=data.index,
                                                open=data['Open'],
                                                high=data['High'],
                                                low=data['Low'],
                                                close=data['Close'])])

            fig.update_layout(
                title=f'{NIFTY_TICKER} Price Chart',
                xaxis_rangeslider_visible=False, # Hides the default range slider below the chart
                xaxis_title="Date",
                yaxis_title="Price (INR)",
                height=600, # Adjust chart height as needed
                template="plotly_dark" # Use a dark theme for the chart
            )
            st.plotly_chart(fig, use_container_width=True)

            # Optional: Display a snippet of the fetched data
            st.subheader("Raw Data Sample")
            st.dataframe(data.tail()) # Show the most recent data points

            # Optional: Update session state for AI summary if needed
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                "ticker": NIFTY_TICKER,
                "date_range": f"{chart_start_date} to {chart_end_date}",
                "chart_status": "Chart generated successfully.",
                "data_points": len(data)
            }


        except Exception as e:
            # Catch more general errors like network issues or unexpected API responses
            st.error(f"An error occurred while fetching or plotting Nifty 50 data: {e}. Please try again.")
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                "ticker": NIFTY_TICKER,
                "date_range": f"{chart_start_date} to {chart_end_date}",
                "chart_status": f"Error: {e}"
            }
else:
    st.info("Select a date range and click 'Get Nifty 50 Chart' to view the candlestick chart.")

st.markdown("---")
