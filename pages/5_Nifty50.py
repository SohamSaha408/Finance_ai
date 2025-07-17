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

end_date = datetime.now().date()
start_date = end_date - timedelta(days=365) # Default to 1 year ago

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date, key="market_trend_start_date")
with col2:
    chart_end_date = st.date_input("End Date", value=end_date, key="market_trend_end_date")

# --- Fetch Market Data Function ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_market_data(ticker, start, end):
    """
    Fetches historical market data for a given ticker from yfinance.
    Includes robust error handling and data type conversion.
    """
    if not ticker:
        st.error("Please enter a ticker symbol.")
        return None

    if start >= end:
        st.error("Start date must be before end date.")
        return None

    try:
        data = yf.download(ticker, start=start, end=end)

        if data.empty:
            st.warning(f"No historical data found for '{ticker}' in the specified date range ({start} to {end}). This could be due to an incorrect ticker, an unsupported date range, or no trading activity.")
            return None

        # --- Robust Data Type Handling for 'Close' (and other columns if needed) ---
        # yfinance can sometimes return single-column data as DataFrame instead of Series.
        # This loop ensures all relevant columns are Series and numeric.
        for col in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']:
            if col in data.columns:
                # If it's a DataFrame with one column, convert to Series
                if isinstance(data[col], pd.DataFrame) and data[col].shape[1] == 1:
                    data[col] = data[col].iloc[:, 0]
                
                # Convert to numeric, coercing errors to NaN
                data[col] = pd.to_numeric(data[col], errors='coerce')
        
        # Drop rows where critical 'Close' data is NaN after conversion
        data.dropna(subset=['Close'], inplace=True)

        if data.empty:
            st.warning(f"No valid data points for '{ticker}' after cleaning (e.g., all 'Close' values were non-numeric).")
            return None

        return data

    except Exception as e:
        # This catches general errors during data fetching (e.g., network issues, invalid ticker)
        st.error(f"An unexpected error occurred while fetching or processing market data for {ticker}: {e}. Please check the ticker symbol, date range, or your internet connection.")
        return None

# --- Main Logic to Display Data ---
if st.button("Get Market Data", key="get_market_data_btn"):
    with st.spinner(f"Fetching raw data for {ticker_symbol}..."):
        market_data = fetch_market_data(ticker_symbol, chart_start_date, chart_end_date)

        if market_data is not None:
            if not market_data.empty:
                st.subheader("--- Raw Data Fetched (Head) ---")
                st.dataframe(market_data.head()) # Show the head of the DataFrame

                st.subheader("--- Raw Data Fetched (Tail) ---")
                st.dataframe(market_data.tail()) # Show the tail of the DataFrame

                st.subheader("--- Raw Data Fetched (Full) ---")
                st.dataframe(market_data) # Show the full DataFrame (Streamlit handles large tables gracefully)
            else:
                st.warning("No data found or all data removed after cleaning.")
        # Error messages are handled inside fetch_market_data function already

st.markdown("---")
