import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

import streamlit as st
import base64
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

# Assuming you have a styling utility, if not, remove or define here
# from utils.styling import set_common_font

# --- Page Configuration ---
st.set_page_config(page_title="Portfolio Tracker", page_icon="💰", layout="wide")

# --- Apply common font if using a utility ---
# set_common_font() # Uncomment if you have this utility

st.title("💰 Portfolio Tracking & Analysis")
st.write("Track your investments, see real-time valuations, and analyze your portfolio's performance.")

st.markdown("---")

# --- Initialize portfolio in session state if it doesn't exist ---
if 'portfolio' not in st.session_state:
    st.session_state['portfolio'] = [] # List of dictionaries, each dict is a holding

# --- Add New Holding Section ---
st.subheader("Add New Holding")
with st.form("new_holding_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        ticker = st.text_input("Ticker Symbol (e.g., AAPL, RELIANCE.NS, ^NSEI)", key="new_ticker").strip().upper()
    with col2:
        shares = st.number_input("Number of Shares/Units", min_value=0.01, value=1.0, step=0.1, key="new_shares")
    with col3:
        purchase_price = st.number_input("Average Purchase Price (per share/unit)", min_value=0.01, value=100.0, step=0.01, key="new_price")
    
    add_button = st.form_submit_button("Add Holding to Portfolio")

    if add_button and ticker and shares > 0 and purchase_price > 0:
        # Check for existing holding to update
        found = False
        for holding in st.session_state['portfolio']:
            if holding['ticker'] == ticker:
                # Simple average for now, could be more complex (e.g., weighted average)
                total_cost_old = holding['shares'] * holding['purchase_price']
                total_cost_new = shares * purchase_price
                total_shares = holding['shares'] + shares
                
                holding['shares'] = total_shares
                holding['purchase_price'] = (total_cost_old + total_cost_new) / total_shares
                st.success(f"Updated {ticker} in portfolio.")
                found = True
                break
        
        if not found:
            st.session_state['portfolio'].append({
                "ticker": ticker,
                "shares": shares,
                "purchase_price": purchase_price,
                "last_price": 0.0, # Will be fetched
                "current_value": 0.0, # Will be calculated
                "gain_loss": 0.0, # Will be calculated
                "percent_gain_loss": 0.0 # Will be calculated
            })
            st.success(f"Added {ticker} to portfolio.")
    elif add_button:
        st.warning("Please fill in all fields to add a holding.")

st.markdown("---")

# --- Portfolio Summary Section ---
st.subheader("Your Current Portfolio Holdings")

if not st.session_state['portfolio']:
    st.info("Your portfolio is empty. Add some holdings using the form above!")
else:
    # --- Fetch current prices ---
    tickers_to_fetch = [h['ticker'] for h in st.session_state['portfolio']]
    
    @st.cache_data(ttl=60*5) # Cache market data for 5 minutes
    def get_current_prices(ticker_list):
        if not ticker_list:
            return {}
        
        # Download data for all tickers, just for the latest day
        # Use period='1d' or '5d' and interval='1d' to get last close
        # yf.download returns a MultiIndex DataFrame for multiple tickers
        data = yf.download(ticker_list, period="1d", interval="1d", progress=False)

        prices = {}
        if data.empty:
            return prices

        # Handle MultiIndex for price data from yfinance for multiple tickers
        # It's usually (Close, Ticker), (Open, Ticker), etc.
        # We want the latest 'Close' price for each ticker
        for ticker in ticker_list:
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    # Try to get the latest 'Close' price for the specific ticker
                    # This targets columns like ('Close', 'AAPL')
                    close_col = ('Close', ticker)
                    if close_col in data.columns:
                        prices[ticker] = data[close_col].iloc[-1]
                    else:
                        # Fallback for indices like ^NSEI which might not have the ticker in MultiIndex
                        # or if it's a single level index from a previous download
                        prices[ticker] = data['Close'].iloc[-1] if 'Close' in data.columns else None
                elif 'Close' in data.columns: # Single-level index, might be for a single ticker only
                    prices[ticker] = data['Close'].iloc[-1]
                else:
                    prices[ticker] = None # Price not found
            except IndexError:
                prices[ticker] = None # No data for this ticker in the fetched period
            except KeyError:
                prices[ticker] = None # Column not found
            except Exception as e:
                st.warning(f"Could not fetch price for {ticker}: {e}")
                prices[ticker] = None
        return prices


    if st.button("Refresh Portfolio Prices", key="refresh_portfolio_btn"):
        st.cache_data.clear() # Clear cache to ensure fresh prices
        current_prices = get_current_prices(tickers_to_fetch)
    else:
        current_prices = get_current_prices(tickers_to_fetch) # Use cached data initially


    total_portfolio_value = 0.0
    total_purchase_cost = 0.0
    
    # Prepare data for display
    portfolio_data = []
    
    for holding in st.session_state['portfolio']:
        ticker = holding['ticker']
        last_price = current_prices.get(ticker)
        
        if last_price is not None and not pd.isna(last_price): # Check for None and NaN
            holding['last_price'] = last_price
            holding['current_value'] = holding['shares'] * last_price
            holding['gain_loss'] = holding['current_value'] - (holding['shares'] * holding['purchase_price'])
            holding['percent_gain_loss'] = (holding['gain_loss'] / (holding['shares'] * holding['purchase_price'])) * 100 if (holding['shares'] * holding['purchase_price']) > 0 else 0
        else:
            holding['last_price'] = "N/A"
            holding['current_value'] = "N/A"
            holding['gain_loss'] = "N/A"
            holding['percent_gain_loss'] = "N/A"

        total_portfolio_value += holding['current_value'] if isinstance(holding['current_value'], (int, float)) else 0
        total_purchase_cost += holding['shares'] * holding['purchase_price']

        portfolio_data.append({
            "Ticker": holding['ticker'],
            "Shares": holding['shares'],
            "Avg. Cost": f"${holding['purchase_price']:.2f}",
            "Last Price": f"${holding['last_price']:.2f}" if isinstance(holding['last_price'], (int, float)) else holding['last_price'],
            "Current Value": f"${holding['current_value']:.2f}" if isinstance(holding['current_value'], (int, float)) else holding['current_value'],
            "Gain/Loss ($)": f"${holding['gain_loss']:.2f}" if isinstance(holding['gain_loss'], (int, float)) else holding['gain_loss'],
            "Gain/Loss (%)": f"{holding['percent_gain_loss']:.2f}%" if isinstance(holding['percent_gain_loss'], (int, float)) else holding['percent_gain_loss']
        })

    if portfolio_data:
        st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True, hide_index=True)
    
    st.markdown(f"**Total Portfolio Value:** ${total_portfolio_value:,.2f}")
    
    total_gain_loss_abs = total_portfolio_value - total_purchase_cost
    total_gain_loss_pct = (total_gain_loss_abs / total_purchase_cost) * 100 if total_purchase_cost > 0 else 0
    
    if total_gain_loss_abs >= 0:
        st.markdown(f"**Total Portfolio Gain/Loss:** <span style='color:green;'>${total_gain_loss_abs:,.2f} ({total_gain_loss_pct:,.2f}%)</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**Total Portfolio Gain/Loss:** <span style='color:red;'>${total_gain_loss_abs:,.2f} ({total_gain_loss_pct:,.2f}%)</span>", unsafe_allow_html=True)


    st.markdown("---")
    
    # --- Diversification Analysis (Basic) ---
    st.subheader("Diversification Breakdown")

    # Basic pie chart for current value allocation
    if total_portfolio_value > 0:
        alloc_data = {
            "Label": [],
            "Value": []
        }
        for holding in st.session_state['portfolio']:
            if isinstance(holding['current_value'], (int, float)):
                alloc_data["Label"].append(holding['ticker'])
                alloc_data["Value"].append(holding['current_value'])
        
        alloc_df = pd.DataFrame(alloc_data)

        if not alloc_df.empty:
            import plotly.express as px
            fig_alloc = px.pie(alloc_df, values='Value', names='Label', 
                               title='Portfolio Allocation by Holding',
                               hole=0.3)
            fig_alloc.update_traces(textinfo='percent+label')
            fig_alloc.update_layout(showlegend=False, template="plotly_dark")
            st.plotly_chart(fig_alloc, use_container_width=True)
        else:
            st.info("Cannot generate allocation chart. No valid current values found.")
    else:
        st.info("Add holdings with valid prices to see diversification analysis.")

    # --- Remove Holding Section ---
    st.subheader("Remove Holding")
    tickers_in_portfolio = [h['ticker'] for h in st.session_state['portfolio']]
    if tickers_in_portfolio:
        ticker_to_remove = st.selectbox("Select Ticker to Remove", [""] + tickers_in_portfolio, key="remove_ticker_select")
        if st.button("Remove Selected Holding", key="remove_btn"):
            if ticker_to_remove:
                st.session_state['portfolio'] = [h for h in st.session_state['portfolio'] if h['ticker'] != ticker_to_remove]
                st.success(f"Removed {ticker_to_remove} from portfolio.")
                st.rerun() # Rerun to update the display immediately
            else:
                st.warning("Please select a ticker to remove.")
    else:
        st.info("No holdings to remove.")
