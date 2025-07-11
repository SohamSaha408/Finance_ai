import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Market Trends Debug", layout="wide")
st.title("📊 Debug: Market Trends Viewer")

ticker = st.text_input("Enter ticker symbol", value="^NSEI").strip().upper()
today = datetime.today().date()
start_date = st.date_input("Start Date", today - timedelta(days=365))
end_date = st.date_input("End Date", today)

if st.button("Fetch Data"):
    try:
        st.write(f"⏳ Fetching data for: `{ticker}` from {start_date} to {end_date}")
        df = yf.download(ticker, start=start_date, end=end_date)

        if df.empty:
            st.warning("⚠ No data returned.")
            st.stop()

        st.write("✅ Data fetched:")
        st.dataframe(df.head())

        # Clean columns
        df = df.fillna(0)
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Log metrics
        st.subheader("Debugging Metrics")
        st.write("First Open:", df['Open'].iloc[0])
        st.write("Last Close:", df['Close'].iloc[-1])
        st.write("Max High:", df['High'].max())
        st.write("Min Low:", df['Low'].min())
        st.write("Total Volume:", df['Volume'].sum())

        open_val = df['Open'].iloc[0]
        close_val = df['Close'].iloc[-1]
        high_val = df['High'].max()
        low_val = df['Low'].min()
        volume = df['Volume'].sum()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Open", f"{open_val:.2f}")
        col2.metric("Close", f"{close_val:.2f}")
        col3.metric("High", f"{high_val:.2f}")
        col4.metric("Low", f"{low_val:.2f}")
        col5.metric("Volume", f"{volume:,.0f}")

        st.subheader("📈 Candlestick Chart")
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
        st.exception(e)
