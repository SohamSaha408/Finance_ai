import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Market Trends Data", page_icon="📈")

st.title("📈 Market Trends Data (Raw Data Only)")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        View raw historical data for Nifty 50 or other stock/index symbols.
    </p>
    """, unsafe_allow_html=True)

st.info("Hint: For Nifty 50, use ticker `^NSEI`. For Reliance Industries, use `RELIANCE.NS`. For Apple, use `AAPL`.")

# --- User Input ---
ticker_symbol = st.text_input(
    "Enter Stock/Index Ticker Symbol (e.g., ^NSEI, RELIANCE.NS):",
    value="^NSEI",
    key="market_trend_ticker_input"
).strip().upper() # Ensure consistent format

# Set default date range to avoid issues with current day's incomplete data
# ⚠️ Note: For current date, sometimes yfinance returns incomplete data or no data until market close.
# Adjusting end_date to yesterday for more consistent results.
end_date = datetime.now().date() - timedelta(days=1)
start_date = end_date - timedelta(days=365) # Default to 1 year ago

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date, key="market_trend_start_date")
with col2:
    chart_end_date = st.date_input("End Date", value=end_date, key="market_trend_end_date")

# --- Fetch Market Data Function ---
@st.cache_data(ttl=3600) # Cache data for 1 hour to reduce API calls
def fetch_market_data(ticker, start, end):
    """
    Fetches historical market data for a given ticker from yfinance.
    Includes robust error handling and data type conversion to prevent TypeErrors.
    """
    if not ticker:
        st.error("Please enter a ticker symbol.")
        return None

    if start >= end:
        st.error("Start date must be before end date.")
        return None

    try:
        # Debugging Stage 1: Before yf.download
        # st.info(f"Attempting to fetch data for {ticker} from {start} to {end}")

        data = yf.download(ticker, start=start, end=end)

        # Debugging Stage 2: After yf.download
        # st.info(f"Data fetched. Type: {type(data)}, Empty: {data.empty}, Columns: {data.columns.tolist() if not data.empty else 'N/A'}")

        if data.empty:
            st.warning(f"No historical data found for '{ticker}' in the specified date range ({start} to {end}). This could be due to an incorrect ticker, an unsupported date range, or no trading activity on these specific dates.")
            return None

        # --- Robust Data Type Handling for DataFrame columns ---
        # Iterate over common numerical columns that yfinance provides
        columns_to_process = ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']
        for col in columns_to_process:
            if col in data.columns:
                # Check if the column is being treated as a DataFrame (e.g., if it's multi-indexed or a single-column DF)
                if isinstance(data[col], pd.DataFrame) and data[col].shape[1] == 1:
                    data[col] = data[col].iloc[:, 0] # Convert single-column DataFrame to Series
                
                # Convert to numeric, coercing any non-numeric values to NaN
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # After converting, drop rows where the 'Close' price is NaN
        # This is critical as 'Close' is often used for plotting/analysis
        data.dropna(subset=['Close'], inplace=True)

        if data.empty:
            st.warning(f"No valid data points remaining for '{ticker}' after cleaning (e.g., all 'Close' values were non-numeric or removed due to NaNs).")
            return None

        return data

    # --- SYNTAX ERROR FIX: Proper 'except' block after 'try' ---
    except Exception as e:
        # This catches general exceptions like network errors, invalid ticker format, etc.
        st.error(f"An unexpected error occurred while fetching or processing market data for '{ticker}': {e}. Please check the ticker symbol, date range, or your internet connection.")
        return None

# --- Main Logic to Display Data ---
if st.button("Get Market Data", key="get_market_data_btn"):
    with st.spinner(f"Fetching raw data for {ticker_symbol}..."):
        market_data = fetch_market_data(ticker_symbol, chart_start_date, chart_end_date)

        if market_data is not None: # Only proceed if data was successfully fetched (not None)
            if not market_data.empty:
                st.subheader("--- Raw Data Fetched (Head) ---")
                st.dataframe(market_data.head()) # Show the head of the DataFrame

                st.subheader("--- Raw Data Fetched (Tail) ---")
                st.dataframe(market_data.tail()) # Show the tail of the DataFrame

                # Only display full DataFrame if it's not excessively large
                if len(market_data) < 500: # Arbitrary limit for full display
                    st.subheader("--- Raw Data Fetched (Full) ---")
                    st.dataframe(market_data)
                else:
                    st.info(f"Full data for {len(market_data)} rows is available, but not displayed here for performance. Head and Tail shown above.")
            else:
                st.warning("No data found or all data removed after cleaning for the selected ticker and date range.")
        # Error messages for fetch failures are already handled inside fetch_market_data

st.markdown("---")
