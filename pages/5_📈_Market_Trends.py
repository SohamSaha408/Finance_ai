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

# --- 1. ASSET SELECTION & CONVERSION DATA ---
TICKERS = {
    # Indices & Commodities
    "Nifty 50": {"symbol": "^NSEI", "currency": "INR", "unit": "Points", "multiplier": 1},
    "Gold (INR)": {"symbol": "GOLDBEES.NS", "currency": "INR", "unit": "per Gram", "multiplier": 100},
    "Silver (INR)": {"symbol": "SILVERBEES.NS", "currency": "INR", "unit": "per Gram", "multiplier": 1},
    
    # Indian Stocks
    "Reliance Industries": {"symbol": "RELIANCE.NS", "currency": "INR", "unit": "per Share", "multiplier": 1},
    "TCS": {"symbol": "TCS.NS", "currency": "INR", "unit": "per Share", "multiplier": 1},

    # US Stocks
    "Tesla": {"symbol": "TSLA", "currency": "USD", "unit": "per Share", "multiplier": 1},
    "Apple": {"symbol": "AAPL", "currency": "USD", "unit": "per Share", "multiplier": 1},
    "Microsoft": {"symbol": "MSFT", "currency": "USD", "unit": "per Share", "multiplier": 1},
    "Google": {"symbol": "GOOGL", "currency": "USD", "unit": "per Share", "multiplier": 1},
    "Amazon": {"symbol": "AMZN", "currency": "USD", "unit": "per Share", "multiplier": 1},
    "NVIDIA": {"symbol": "NVDA", "currency": "USD", "unit": "per Share", "multiplier": 1},
}

asset_name = st.selectbox("Select an Asset to Monitor", options=list(TICKERS.keys()))
selected_asset = TICKERS[asset_name]
selected_ticker = selected_asset["symbol"]

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
                st.warning(f"No data found for {asset_name} in the specified date range.")
            else:
                # Apply price conversion/multiplier if necessary
                multiplier = selected_asset["multiplier"]
                if multiplier != 1:
                    price_cols = ['Open', 'High', 'Low', 'Close']
                    for col in price_cols:
                        if col in data.columns:
                            data[col] = data[col] * multiplier
                
                # Calculate daily and percentage changes
                data['Daily_Change'] = data['Close'].diff()
                data['Pct_Change'] = data['Close'].pct_change() * 100

                st.subheader(f"{asset_name} Closing Price Trend")

                fig = go.Figure(data=[go.Scatter(
                    x=data.index, y=data['Close'], mode='lines',
                    name=f'{asset_name} Close', line=dict(color='cyan'), connectgaps=True
                )])

                fig.add_trace(go.Scatter(
                    x=data[data['Daily_Change'] >= 0].index, y=data[data['Daily_Change'] >= 0]['Close'],
                    mode='markers', name='Profit', marker=dict(symbol='triangle-up', color='green', size=8)
                ))
                fig.add_trace(go.Scatter(
                    x=data[data['Daily_Change'] < 0].index, y=data[data['Daily_Change'] < 0]['Close'],
                    mode='markers', name='Loss', marker=dict(symbol='triangle-down', color='red', size=8)
                ))

                for index, row in data.iterrows():
                    pct_change = row['Pct_Change']
                    if pd.notna(pct_change) and abs(pct_change) > 1.0:
                        color = "green" if pct_change > 0 else "red"
                        y_anchor = "bottom" if pct_change > 0 else "top"
                        text = f"+{pct_change:.2f}%" if pct_change > 0 else f"{pct_change:.2f}%"
                        y_shift = 15 if pct_change > 0 else -15
                        
                        fig.add_annotation(
                            x=index, y=row['Close'], text=text, showarrow=False,
                            font=dict(color=color, size=10), yanchor=y_anchor, yshift=y_shift
                        )

                # Update y-axis title dynamically
                yaxis_title = f"Price ({selected_asset['unit']}) ({selected_asset['currency']})"
                
                fig.update_layout(
                    title=f'{asset_name} ({selected_ticker}) Closing Price Trend',
                    xaxis_rangeslider_visible=True,
                    xaxis_title="Date", yaxis_title=yaxis_title,
                    height=600, template="plotly_dark", showlegend=True
                )
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")
