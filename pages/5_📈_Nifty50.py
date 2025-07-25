import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import base64
import os

# --- Page Configuration (must be the first Streamlit command) ---
st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈", layout="wide")

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
st.write("View the historical performance of the Nifty 50 index over a selected date range.")

# --- Define Ticker and Date Range ---
NIFTY_TICKER = "^NSEI"
end_date = datetime.now().date() - timedelta(days=1)
start_date = end_date - timedelta(days=365)

col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", value=start_date, key="nifty_chart_start_date")
with col2:
    chart_end_date = st.date_input("End Date", value=end_date, key="nifty_chart_end_date")

# --- Fetch and Display Chart Button ---
if st.button("Get Nifty 50 Chart", key="get_nifty_chart_btn"):
    if chart_start_date >= chart_end_date:
        st.error("Error: Start date must be before end date.")
    else:
        with st.spinner(f"Fetching historical data for Nifty 50..."):
            try:
                data = yf.download(NIFTY_TICKER, start=chart_start_date, end=chart_end_date)
                
                # --- FIX: FLATTEN MULTI-LEVEL COLUMNS ---
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.droplevel(1)
                
                if data.empty:
                    st.warning(f"No data found for Nifty 50 in the specified date range.")
                else:
                    st.subheader(f"Nifty 50 Closing Price Trend ({chart_start_date} to {chart_end_date})")

                    fig = go.Figure(data=[go.Scatter(
                        x=data.index,
                        y=data['Close'],
                        mode='lines',
                        name='Nifty 50 Close',
                        line=dict(color='cyan'),
                        connectgaps=True 
                    )])
                    
                    fig.update_layout(
                        title=f'{NIFTY_TICKER} Closing Price Trend',
                        xaxis_rangeslider_visible=True,
                        xaxis_title="Date",
                        yaxis_title="Closing Price (INR)",
                        height=600,
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.info("Select a date range and click 'Get Nifty 50 Chart' to view the trend.")

st.markdown("---")
