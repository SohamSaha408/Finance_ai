# pages/2_Watchlist.py
import streamlit as st
import sqlite3
import yfinance as yf # Import the yfinance library

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


# --- Page configuration ---
st.set_page_config(page_title="My Watchlist", page_icon="⭐", layout="wide")

# --- Authentication check ---
if not st.session_state.get("logged_in", False):
    st.error("Please log in to view your watchlist.")
    st.stop()

st.title("⭐ My Stock Watchlist")

# --- Database Connection ---
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
user_id = st.session_state.get("user_id")

# --- Sidebar Form to Add Ticker ---
with st.sidebar:
    st.header("Add a New Ticker")
    with st.form("add_ticker_form", clear_on_submit=True):
        new_ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):").upper()
        submitted = st.form_submit_button("Add to Watchlist")
        
        if submitted and new_ticker:
            try:
                # Check if ticker is valid before adding
                ticker_data = yf.Ticker(new_ticker)
                if ticker_data.history(period="1d").empty:
                    st.warning(f"Ticker '{new_ticker}' seems invalid. Please check and try again.")
                else:
                    cursor.execute("INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)", (user_id, new_ticker))
                    conn.commit()
                    st.success(f"Added {new_ticker} to your watchlist!")
            except Exception as e:
                st.error(f"Failed to add ticker: {e}")

# --- Display Current Watchlist with Live Data ---
st.header("Live Market Data")
cursor.execute("SELECT id, ticker FROM watchlist WHERE user_id = ?", (user_id,))
watchlist_items = cursor.fetchall()

if not watchlist_items:
    st.info("Your watchlist is empty. Add a ticker using the form in the sidebar.")
else:
    # Create columns for the dashboard layout
    cols = st.columns(3) 
    col_index = 0

    for item_id, ticker in watchlist_items:
        try:
            # Fetch data for the ticker
            data = yf.Ticker(ticker)
            info = data.info
            
            # Extract key metrics
            price = info.get("currentPrice", 0)
            prev_close = info.get("previousClose", 1)
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            # Display data in the next available column
            with cols[col_index]:
                st.subheader(f"{info.get('longName', ticker)} ({ticker})")
                st.metric(label="Current Price", value=f"${price:,.2f}", delta=f"{change:,.2f} ({change_percent:.2f}%)")
                
                if st.button("Remove", key=f"remove_{item_id}", use_container_width=True):
                    cursor.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
                    conn.commit()
                    st.rerun()

            # Move to the next column, wrap around if necessary
            col_index = (col_index + 1) % len(cols)

        except Exception as e:
            with cols[col_index]:
                st.error(f"Could not fetch data for {ticker}.")
            col_index = (col_index + 1) % len(cols)

# --- Close the database connection ---
conn.close()
