import streamlit as st
import yfinance as yf
import pandas as pd

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(page_title="\ud83d\udcc8 Stock Screener", layout="wide")
st.title("\ud83d\udcc8 Live Stock Screener (Custom Filters)")

# -----------------------
# Sidebar Filters
# -----------------------
st.sidebar.header("\ud83e\uddf0 Stock Screener Filters")

sectors = ['All', 'Technology', 'Financial Services', 'Healthcare', 'Energy', 'Industrials', 'Consumer Defensive']
selected_sector = st.sidebar.selectbox("Sector", sectors)

pe_min, pe_max = st.sidebar.slider("P/E Ratio", 0.0, 100.0, (0.0, 50.0))
price_min, price_max = st.sidebar.slider("Price Range ($)", 0.0, 1500.0, (10.0, 500.0))
market_caps = ['All', 'Small', 'Mid', 'Large']
selected_cap = st.sidebar.radio("Market Cap", market_caps)

# -----------------------
# Load Tickers (Sample S&P 500)
# -----------------------
@st.cache_data
def load_tickers():
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
    df = pd.read_csv(url)
    return df

tickers_df = load_tickers()

# -----------------------
# Helper: Categorize Market Cap
# -----------------------
def cap_category(market_cap):
    if market_cap is None:
        return 'Unknown'
    if market_cap < 2e9:
        return 'Small'
    elif market_cap < 10e9:
        return 'Mid'
    else:
        return 'Large'

# -----------------------
# Fetch Data from Yahoo Finance
# -----------------------
@st.cache_data(show_spinner=True)
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "name": info.get("shortName", "N/A"),
            "price": info.get("regularMarketPrice", 0),
            "pe": info.get("trailingPE", 0),
            "sector": info.get("sector", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "cap_category": cap_category(info.get("marketCap", 0))
        }
    except Exception:
        return None

with st.spinner("\ud83d\udce1 Fetching stock data..."):
    stock_data = []
    for _, row in tickers_df.iterrows():
        data = fetch_stock_data(row['Symbol'])
        if data:
            stock_data.append(data)

df = pd.DataFrame(stock_data)

# -----------------------
# Apply Filters
# -----------------------
filtered_df = df[
    (df['price'] >= price_min) & (df['price'] <= price_max) &
    (df['pe'] >= pe_min) & (df['pe'] <= pe_max)
]

if selected_sector != 'All':
    filtered_df = filtered_df[filtered_df['sector'] == selected_sector]

if selected_cap != 'All':
    filtered_df = filtered_df[filtered_df['cap_category'] == selected_cap]

# -----------------------
# Display Results
# -----------------------
st.subheader(f"\ud83d\udcc8 {len(filtered_df)} Stocks Matching Your Criteria")
st.dataframe(filtered_df[['ticker', 'name', 'price', 'pe', 'sector', 'cap_category']], use_container_width=True)

# -----------------------
# Optional AI Summary
# -----------------------
if not filtered_df.empty:
    top_sectors = filtered_df['sector'].value_counts().nlargest(2).index.tolist()
    insight = f"\ud83d\udd0d Out of {len(df)} stocks, **{len(filtered_df)}** match your filters. Most are from the **{', '.join(top_sectors)}** sector(s)."
else:
    insight = "\u26a0\ufe0f No stocks match your current filter settings. Try widening the range."

st.markdown("---")
st.markdown(f"**\ud83e\udde0 AI Summary:** {insight}")
