import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go
from utils.styling import set_common_font # Adjust path if your utils folder is structured differently
import streamlit as st
import base64

# --- Function to get base64 encoded image ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Path to your background image ---
# IMPORTANT: Make sure 'black-particles-background.avif' is in the correct directory
# relative to where your Streamlit app is run from.
# For example, if it's in a subfolder named 'images', the path would be "images/black-particles-background.avif".
background_image_path = "black-particles-background.avif" # Updated path

# --- Get the base64 encoded string and inject CSS ---
try:
    encoded_image = get_base64_image(background_image_path)
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{encoded_image}"); /* Changed mime type to avif */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"Error: Background image not found at '{background_image_path}'. Please check the path for this page.")
except Exception as e:
    st.error(f"An error occurred while setting the background image for this page: {e}")

# --- Your page-specific content starts here ---
# (e.g., st.title, st.write, input widgets, charts, etc.)

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈")


st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈", layout="wide")
st.title("📈 Nifty 50 Historical Chart")
st.write("View the historical performance of the Nifty 50 index. This chart provides candlestick visualization of price movements over your selected date range, helping you analyze market trends.")
# ... rest of your page code ...
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
            # Fetch data using yfinance
            data = yf.download(NIFTY_TICKER, start=chart_start_date, end=chart_end_date)

            # Handle multi-level columns if they exist (e.g., from yfinance output)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

            if data.empty:
                st.warning(f"No historical data found for Nifty 50 in the specified date range ({chart_start_date} to {chart_end_date}). This could be due to no trading activity on selected dates (e.g., holidays) or an incorrect ticker.")
                st.stop()

            if 'Close' not in data.columns:
                st.error("Error: 'Close' price column not found in fetched data. Cannot plot the trend. Available columns: " + ", ".join(data.columns.tolist()))
                st.stop()

            # Ensure 'Close' column is a Series and numeric
            close_series = data['Close']
            if isinstance(close_series, pd.DataFrame) and close_series.shape[1] == 1:
                close_series = close_series.iloc[:, 0]
            
            data['Close'] = pd.to_numeric(close_series, errors='coerce')
            data.dropna(subset=['Close'], inplace=True) 

            if data['Close'].empty:
                st.warning("No valid 'Close' price data available for plotting after cleaning.")
                st.stop()

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

            # Update session state for AI summary if needed
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                "ticker": NIFTY_TICKER,
                "date_range": f"{chart_start_date} to {chart_end_date}",
                "chart_status": "Chart generated successfully.",
                "data_points": len(data)
            }

        except Exception as e:
            st.error(f"An error occurred while fetching or plotting Nifty 50 data: {e}. Please try again.")
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
