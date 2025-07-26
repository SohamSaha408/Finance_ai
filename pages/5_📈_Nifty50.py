import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import base64
import os

# --- Page Configuration (must be the first Streamlit command) ---
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

# --- Asset Selection ---
TICKERS = {
    "Nifty 50": {"symbol": "^NSEI", "currency": "INR"},
    "Gold (INR)": {"symbol": "GOLDBEES.NS", "currency": "INR"},
    "Silver (INR)": {"symbol": "SILVERBEES.NS", "currency": "INR"}
}

asset_name = st.selectbox("Select an Asset to Monitor", options=list(TICKERS.keys()))
selected_ticker = TICKERS[asset_name]["symbol"]
selected_currency = TICKERS[asset_name]["currency"]

# --- Page Content ---
st.title(f"📈 {asset_name} Historical Chart")
st.write(f"View the historical performance of {asset_name} with daily profit/loss indicators.")

# --- Date Range Selection ---
end
