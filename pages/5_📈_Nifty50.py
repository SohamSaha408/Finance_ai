import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import base64
import os

# --- Page Configuration ---
st.set_page_config(page_title="Market Chart", page_icon="📈", layout="wide")

# --- Helper function for background image ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# --- Set Background ---
encoded_image = get_base64_image("black-particles-background.avif")
if encoded_image:
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# --- 1. ASSET SELECTION ---
TICKERS = {
    "Nifty 50": {"symbol": "^NSEI", "currency": "INR"},
    "Gold": {"symbol": "GOLDBEES.NS", "currency": "INR"},
    "Silver": {"symbol": "SILVERBEES.NS", "currency": "INR"}
}

asset_name = st.selectbox("Select an Asset to Monitor", options=list(TICKERS.keys()))
selected_ticker = TICKERS[asset_name]["symbol"]
selected_currency = TICKERS[asset_name]["currency"]

# --- Page Content ---
st.title(f"📈 {asset_name} Historical Chart")
st.write(f"View the historical performance of {asset_name} with daily profit/loss indicators.")

# --- Date Range Selection ---
end_date = datetime.now().date()
start_date = end_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date)
with col2:
    chart_end_date = st.date_input("End Date", value=end_date)

st.markdown("---")

# --- Chart Generation Logic ---
if chart_start_date >= chart_end_date:
    st.error("Error: Start date must be before end date.")
else:
    with st.spinner(f"Fetching historical data for {asset_name}..."):
        try:
            data = yf.download(selected_ticker, start=chart_start_date, end=chart_end_date)
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            if data.empty:
                st.warning(f"
