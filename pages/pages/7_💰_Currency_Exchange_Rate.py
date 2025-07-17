import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np # For numerical operations and NaN handling

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Custom Currency Exchange Rates", page_icon="💰")

st.title("💰 Custom Currency Exchange Rates")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Compare the historical exchange rate between any two selected currencies.
    </p>
    """, unsafe_allow_html=True)

# --- Define 16 Common Currencies and their USD-based tickers ---
# 'is_base_vs_usd': True means ticker gives Currency/USD (e.g., EURUSD=X gives EUR per USD)
# 'is_base_vs_usd': False means ticker gives USD/Currency (e.g., INR=X gives INR per USD)
# USD does not have a ticker itself, as it's the implicit base for many.
CURRENCY_TICKER_MAP = {
    'USD': {'ticker': None, 'is_base_vs_usd': True}, # USD is the reference currency
    'EUR': {'ticker': 'EURUSD=X', 'is_base_vs_usd': True}, # EUR per USD
    'GBP': {'ticker': 'GBPUSD=X', 'is_base_vs_usd': True}, # GBP per USD
    'JPY': {'ticker': 'JPY=X', 'is_base_vs_usd': False}, # JPY per USD (i.e., USD per JPY is 1/JPY=X)
    'CAD': {'ticker': 'CAD=X', 'is_base_vs_usd': False}, # CAD per USD (i.e., USD per CAD is 1/CAD=X)
    'AUD': {'ticker': 'AUDUSD=X', 'is_base_vs_usd': True}, # AUD per USD
    'CHF': {'ticker': 'CHF=X', 'is_base_vs_usd': False}, # CHF per USD (i.e., USD per CHF is 1/CHF=X)
    'INR': {'ticker': 'INR=X', 'is_base_vs_usd': False}, # INR per USD (i.e., USD per INR is 1/INR=X)
    'CNY': {'ticker': 'CNY=X', 'is_base_vs_usd': False}, # CNY per USD
    'BRL': {'ticker': 'BRL=X', 'is_base_vs_usd': False}, # BRL per USD
    'ZAR': {'ticker': 'ZAR=X', 'is_base_vs_usd': False}, # ZAR per USD
    'MXN': {'ticker': 'MXN=X', 'is_base_vs_usd': False}, # MXN per USD
    'SGD': {'ticker': 'SGD=X', 'is_base_vs_usd': False}, # SGD per USD
    'HKD': {'ticker': 'HKD=X', 'is_base_vs_usd': False}, # HKD per USD
    'KRW': {'ticker': 'KRW=X', 'is_base_vs_usd': False}, # KRW per USD
    'RUB': {'ticker': 'RUB=X', 'is_base_vs_usd': False}, # RUB per USD (Note: Data might be volatile/limited due to sanctions)
}

ALL_CURRENCIES = sorted(list(CURRENCY_TICKER_MAP.keys()))

# --- User Selection for Base and Quote Currencies ---
col1_curr, col2_curr = st.columns(2)
with col1_curr:
    base_currency = st.selectbox(
        "Select Base Currency (1 unit of this currency...)",
        options=ALL_CURRENCIES,
        index=ALL_CURRENCIES.index('USD'), # Default to USD
        key="base_currency_select"
    )
with col2_curr:
    quote_currency = st.selectbox(
        "...equals how many units of this currency?",
        options=ALL_CURRENCIES,
        index=ALL_CURRENCIES.index('INR'), # Default to INR
        key="quote_currency_select"
    )

if base_currency == quote_currency:
    st.warning("Base and Quote currencies cannot be the same. Please select different currencies.")
    st.stop()

# --- Date Range Selection ---
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365 * 2) # Default to 2 years of data

col1_date, col2_date = st.columns(2)
with col1_date:
    chart_start_date = st.date_input("Start Date", value=start_date, key="custom_exchange_start_date")
with col2_date:
    chart_end_date = st.date_input("End Date", value=end_date, key="custom_exchange_end_date")

# --- Fetch Data and Calculate Cross Rate Function ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_and_calculate_exchange_rate(base_curr, quote_curr, start, end):
    """
    Fetches required currency data from yfinance and calculates the cross rate.
    Returns a DataFrame with 'Close' prices for the desired pair.
    """
    data = pd.DataFrame(index=pd.bdate_range(start=start, end=end, freq='B')) # Business days index
    data.index.name = 'Date'

    tickers_to_fetch = []
    base_info = CURRENCY_TICKER_MAP[base_curr]
    quote_info = CURRENCY_TICKER_MAP[quote_curr]

    # Determine which tickers are needed
    if base_info['ticker']:
        tickers_to_fetch.append(base_info['ticker'])
    if quote_info['ticker'] and quote_info['ticker'] != base_info['ticker']: # Avoid fetching same ticker twice
        tickers_to_fetch.append(quote_info['ticker'])

    if not tickers_to_fetch and (base_curr != 'USD' and quote_curr != 'USD'):
        # This case should ideally not happen if both non-USD currencies have tickers against USD
        st.error(f"Cannot determine tickers for {base_curr}/{quote_curr} pair.")
        return None

    fetched_raw_data = {}
    for ticker in set(tickers_to_fetch): # Use set to avoid duplicate fetches
        df_temp = yf.download(ticker, start=start, end=end)
        if not df_temp.empty and 'Close' in df_temp.columns:
            fetched_raw_data[ticker] = df_temp['Close']
        else:
            st.warning(f"Could not fetch data for ticker: {ticker}. This may affect the exchange rate calculation.")
            return None # Stop if crucial data is missing

    if not fetched_raw_data and (base_curr != 'USD' and quote_curr != 'USD'):
        st.warning("No data fetched for the selected non-USD currencies.")
        return None

    # Merge all fetched data onto a common date index
    for ticker, series in fetched_raw_data.items():
        data = data.join(series.rename(ticker))

    # Drop dates where any required data is missing for calculation
    data.dropna(inplace=True)

    if data.empty:
        st.warning(f"No common data points found for {base_curr}/{quote_curr} in the specified date range after merging and cleaning.")
        return None

    # --- Calculate the target exchange rate ---
    final_rates = pd.Series(index=data.index, dtype=float)

    # Convert all needed rates to CURRENCY_X / USD
    # For example, if JPY=X gives USD/JPY, then JPY/USD = 1 / JPY=X.
    # If EURUSD=X gives EUR/USD, then EUR/USD is simply EURUSD=X.

    base_rate_vs_usd = None
    if base_curr == 'USD':
        base_rate_vs_usd = pd.Series(1.0, index=data.index) # USD/USD is 1
    else:
        base_ticker = base_info['ticker']
        if base_ticker in data.columns:
            if base_info['is_base_vs_usd']: # e.g., EUR/USD
                base_rate_vs_usd = data[base_ticker]
            else: # e.g., USD/JPY -> JPY=X. We need JPY/USD = 1 / (JPY=X)
                base_rate_vs_usd = 1 / data[base_ticker]
        else:
            st.warning(f"Missing data for base currency '{base_curr}' ticker '{base_ticker}'.")
            return None


    quote_rate_vs_usd = None
    if quote_curr == 'USD':
        quote_rate_vs_usd = pd.Series(1.0, index=data.index) # USD/USD is 1
    else:
        quote_ticker = quote_info['ticker']
        if quote_ticker in data.columns:
            if quote_info['is_base_vs_usd']: # e.g., GBP/USD
                quote_rate_vs_usd = data[quote_ticker]
            else: # e.g., USD/INR -> INR=X. We need INR/USD = 1 / (INR=X)
                quote_rate_vs_usd = 1 / data[quote_ticker]
        else:
            st.warning(f"Missing data for quote currency '{quote_curr}' ticker '{quote_ticker}'.")
            return None

    # Calculate Base/Quote = (Base/USD) / (Quote/USD)
    if base_rate_vs_usd is not None and quote_rate_vs_usd is not None:
        # Ensure indices align before division
        aligned_rates = pd.concat([base_rate_vs_usd.rename('base_vs_usd'),
                                   quote_rate_vs_usd.rename('quote_vs_usd')], axis=1).dropna()
        if not aligned_rates.empty:
            final_rates = aligned_rates['base_vs_usd'] / aligned_rates['quote_vs_usd']
        else:
            st.warning("No aligned data points after fetching and preparing rates for calculation.")
            return None
    else:
        st.warning("Could not obtain necessary rates for calculation.")
        return None

    if final_rates.empty:
        st.warning(f"No valid calculated exchange rates for {base_curr}/{quote_curr}.")
        return None

    return pd.DataFrame(final_rates.rename('Close')) # Return as DataFrame with 'Close' column


# --- Main Execution ---
if st.button("Get Exchange Rate Chart", key="get_custom_exchange_chart_btn"):
    if chart_start_date >= chart_end_date:
        st.error("Error: Start date must be before end date. Please adjust the dates.")
        st.stop()

    with st.spinner(f"Fetching and calculating {base_currency}/{quote_currency} exchange rates..."):
        exchange_data = fetch_and_calculate_exchange_rate(
            base_currency, quote_currency, chart_start_date, chart_end_date
        )

        if exchange_data is not None and not exchange_data.empty:
            # --- Line Chart Generation ---
            st.subheader(f"{base_currency}/{quote_currency} Exchange Rate ({chart_start_date} to {chart_end_date})")

            fig = go.Figure(data=[go.Scatter(x=exchange_data.index, y=exchange_data['Close'], mode='lines', name=f'{base_currency}/{quote_currency} Rate')])

            fig.update_layout(
                title=f'{base_currency}/{quote_currency} Exchange Rate (1 {base_currency} = X {quote_currency})',
                xaxis_title="Date",
                yaxis_title=f"Exchange Rate ({quote_currency} per 1 {base_currency})",
                hovermode="x unified",
                height=500,
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Optional: Display a snippet of the fetched data
            st.subheader("Calculated Exchange Rate Sample")
            st.dataframe(exchange_data.tail())

            latest_rate = exchange_data['Close'].iloc[-1]
            st.info(f"Latest exchange rate on {exchange_data.index[-1].date()}: 1 **{base_currency}** = **{latest_rate:,.4f} {quote_currency}**")

        else:
            st.error("Could not generate the exchange rate chart. Please check your selections and date range.")
else:
    st.info("Select base and quote currencies and a date range, then click 'Get Exchange Rate Chart' to view the trend.")

st.markdown("---")
