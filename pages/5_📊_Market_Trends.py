import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Market Trends Data", page_icon="📊", layout="wide")

st.title("📊 Market Trends Data (with Candlestick Chart)")
st.markdown(
    """
    <p style='font-size: 1.1rem;'>Fetch and view historical stock/index data with metrics and candlestick chart.</p>
    """,
    unsafe_allow_html=True
)

st.info("Hint: For Nifty 50 use `^NSEI`, for Reliance use `RELIANCE.NS`, for Apple use `AAPL`.")

# User Inputs
ticker = st.text_input("Enter Ticker Symbol_
