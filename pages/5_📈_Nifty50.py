import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import base64
import os

# --- Page Configuration ---
st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈", layout="wide")

# --- Authentication Check ---
# if not st.session_state.get("logged_in", False):
#     st.error("Please log in to view this page.")
#     st.stop()

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

# --- Page Content ---
st.title("📈 Nifty 50 Historical Chart")
st.write("View the historical performance of the Nifty 50 index with daily profit/loss indicators.")

# --- Define Ticker and Date Range ---
NIFTY_TICKER = "^NSEI"
end_date = datetime.now().date() - timedelta(days=1)
start_date = end_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date, key="nifty_chart_start_date")
with col2:
    chart_end_date = st.date_input("End Date", value=end_date, key="nifty_chart_end_date")

# --- Chart Generation Logic (now runs automatically) ---
if chart_start_date >= chart_end_date:
    st.error("Error: Start date must be before end date.")
else:
    with st.spinner(f"Fetching historical data for Nifty 50..."):
        try:
            data = yf.download(NIFTY_TICKER, start=chart_start_date, end=chart_end_date)
            
            if data.empty:
                st.warning("No historical data found for Nifty 50 in the specified date range.")
            else:
                data['Daily_Change'] = data['Close'].diff()

                fig = go.Figure(data=[go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Nifty 50 Close',
                    line=dict(color='#00C853')
                    connectgaps=True  # This new line fixes the issue
                )])

                fig.add_trace(go.Scatter(
                    x=data[data['Daily_Change'] >= 0].index,
                    y=data[data['Daily_Change'] >= 0]['Close'],
                    mode='markers',
                    name='Profit',
                    marker=dict(symbol='triangle-up', color='green', size=10)
                ))

                fig.add_trace(go.Scatter(
                    x=data[data['Daily_Change'] < 0].index,
                    y=data[data['Daily_Change'] < 0]['Close'],
                    mode='markers',
                    name='Loss',
                    marker=dict(symbol='triangle-down', color='red', size=10)
                ))

                fig.update_layout(
                    title=f'{NIFTY_TICKER} Closing Price Trend with Daily Changes',
                    xaxis_rangeslider_visible=True,
                    xaxis_title="Date",
                    yaxis_title="Closing Price (INR)",
                    height=600,
                    template="plotly_dark",
                    showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
