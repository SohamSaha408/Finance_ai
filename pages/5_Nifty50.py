import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈")

st.title("📈 Nifty 50 Price Trend")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Visualize the historical closing price trend of the Nifty 50 index.
    </p>
    """, unsafe_allow_html=True)

# --- Define the Nifty 50 Ticker ---
NIFTY_TICKER = "^NSEI" # Standard ticker for Nifty 50

# --- Date Range Selection ---
# Adjusting end_date to yesterday for more consistent results,
# as yfinance might not have complete data for the current day until market close.
end_date = datetime.now().date() - timedelta(days=1)
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
            # --- DEBUGGING STAGE 1: Before yf.download ---
            st.info("Debugging Stage 1: Initiating data fetch.")
            st.write(f"Fetching Ticker: **{NIFTY_TICKER}**")
            st.write(f"Requested Start Date: **{chart_start_date}**")
            st.write(f"Requested End Date: **{chart_end_date}**")

            # Fetch data using yfinance
            data = yf.download(NIFTY_TICKER, start=chart_start_date, end=chart_end_date)

            # --- DEBUGGING STAGE 2: After yf.download, before any validation ---
            st.info("Debugging Stage 2: Data fetched from yfinance.")
            st.write(f"Type of 'data' object: **{type(data)}**")
            st.write(f"Is 'data' DataFrame empty? **{data.empty}**")

            if isinstance(data, pd.DataFrame):
                st.write(f"Columns in 'data': **{data.columns.tolist()}**") # Show columns as list
                st.write(f"Shape of 'data' DataFrame: **{data.shape}**")
                if not data.empty:
                    st.write("Head of 'data' DataFrame:")
                    st.dataframe(data.head()) # Display as dataframe
                else:
                    st.write("DataFrame is empty after yf.download.")
            else:
                st.error("Error: yf.download did not return a Pandas DataFrame. Cannot proceed.")
                st.stop()

            # --- CRITICAL FIX: Flatten multi-level columns if they exist ---
            # This happens when yfinance returns data with (column_name, ticker_symbol)
            # as column names, often if multiple tickers were requested or due to yfinance versioning.
            if isinstance(data.columns, pd.MultiIndex):
                # Attempt to get the lower level column names, e.g., 'Close' from ('Close', '^NSEI')
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
                st.info("Detected and flattened multi-level column index.")
                st.write(f"New Columns after flattening: **{data.columns.tolist()}**")


            # --- CRITICAL VALIDATION 1: Check if DataFrame is empty ---
            if data.empty:
                st.warning(f"No historical data found for Nifty 50 in the specified date range ({chart_start_date} to {chart_end_date}). This could be due to no trading activity on selected dates (e.g., holidays) or an incorrect ticker.")
                st.stop() # Stop further execution if no data

            # --- DEBUGGING STAGE 3: After initial empty check, before Close column check ---
            st.info("Debugging Stage 3: DataFrame is not empty. Checking 'Close' column.")
            st.write(f"'Close' column exists? {'Close' in data.columns}")

            # Ensure 'Close' column exists
            if 'Close' not in data.columns:
                st.error("Error: 'Close' price column not found in fetched data. Cannot plot the trend. Available columns: " + ", ".join(data.columns.tolist()))
                st.stop()

            # --- DEBUGGING STAGE 4: Before and after pd.to_numeric and dropna ---
            st.info("Debugging Stage 4: Processing 'Close' column.")

            # Ensure 'data['Close']' is a Series before processing.
            # While previous debug showed it's Series, this is a safety for edge cases.
            close_series = data['Close']
            if isinstance(close_series, pd.DataFrame) and close_series.shape[1] == 1:
                close_series = close_series.iloc[:, 0]
            
            st.write(f"Type of 'close_series' before to_numeric: **{type(close_series)}**")
            if not close_series.empty:
                st.write(f"First 5 'Close' values before to_numeric: **{close_series.head().tolist()}**")
            
            close_series = pd.to_numeric(close_series, errors='coerce')
            st.write(f"Type of 'close_series' after to_numeric: **{type(close_series)}**")
            if not close_series.empty:
                st.write(f"First 5 'Close' values after to_numeric: **{close_series.head().tolist()}**")

            # Update the 'Close' column in the main DataFrame with the processed Series
            data['Close'] = close_series

            # Drop rows where 'Close' is NaN after conversion
            data.dropna(subset=['Close'], inplace=True) 
            st.write(f"Is 'data[\"Close\"]' empty after dropna? **{data['Close'].empty}**")

            if data['Close'].empty:
                st.warning("No valid 'Close' price data available for plotting after cleaning.")
                st.stop()

            # --- DEBUGGING STAGE 5: Final check before plotting ---
            st.info("Debugging Stage 5: Data ready for plotting.")
            st.write(f"Type of data.index: **{type(data.index)}**")
            st.write(f"Length of data.index: **{len(data.index)}**")
            if not data.index.empty:
                st.write(f"First 5 elements of data.index: **{data.index[:5].tolist()}**")
            
            st.write(f"Type of data['Close']: **{type(data['Close'])}**")
            st.write(f"Length of data['Close']: **{len(data['Close'])}**")
            if not data['Close'].empty:
                st.write(f"First 5 elements of data['Close']: **{data['Close'].head().tolist()}**")

            # --- Line Chart Generation ---
            st.subheader(f"Nifty 50 Closing Price Trend ({chart_start_date} to {chart_end_date})")

            fig = go.Figure(data=[go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Nifty 50 Close')])

            fig.update_layout(
                title=f'{NIFTY_TICKER} Closing Price Trend',
                xaxis_rangeslider_visible=True,
                xaxis_title="Date",
                yaxis_title="Closing Price (INR)",
                height=600,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Optional: Display a snippet of the fetched data
            st.subheader("Raw Data Sample")
            st.dataframe(data.tail())

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
            # This general exception catches any error not specifically handled
            st.error(f"An error occurred while fetching or plotting Nifty 50 data: {e}. Please try again.")
            st.info("Please copy the full error message and any debugging info shown above this error message.")
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                "ticker": NIFTY_TICKER,
                "date_range": f"{chart_start_date} to {chart_end_date}",
                "chart_status": f"Error: {e}"
            }
else:
    st.info("Select a date range and click 'Get Nifty 50 Chart' to view the closing price trend.")

st.markdown("---")
