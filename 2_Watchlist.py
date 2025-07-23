# pages/2_Watchlist.py
import streamlit as st
import sqlite3

# --- Page configuration ---
st.set_page_config(page_title="My Watchlist", page_icon="⭐")

# --- Authentication check ---
if not st.session_state.get("logged_in", False):
    st.error("Please log in to view your watchlist.")
    st.stop()

st.title("⭐ My Stock Watchlist")

# --- Database Connection ---
conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# Get the current user's ID
user_id = st.session_state.get("user_id")

# --- Add Ticker to Watchlist Form ---
st.header("Add a New Ticker")
with st.form("add_ticker_form", clear_on_submit=True):
    new_ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, GOOGL):").upper()
    submitted = st.form_submit_button("Add to Watchlist")
    
    if submitted and new_ticker:
        try:
            cursor.execute("INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)", (user_id, new_ticker))
            conn.commit()
            st.success(f"Added {new_ticker} to your watchlist!")
        except Exception as e:
            st.error(f"Failed to add ticker: {e}")

# --- Display Current Watchlist ---
st.header("Your Current Watchlist")
cursor.execute("SELECT id, ticker FROM watchlist WHERE user_id = ?", (user_id,))
watchlist_items = cursor.fetchall()

if not watchlist_items:
    st.info("Your watchlist is empty. Add a ticker using the form above.")
else:
    for item_id, ticker in watchlist_items:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**{ticker}**")
        with col2:
            if st.button("Remove", key=f"remove_{item_id}"):
                cursor.execute("DELETE FROM watchlist WHERE id = ?", (item_id,))
                conn.commit()
                st.rerun()

# --- Close the database connection ---
conn.close()
