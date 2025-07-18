import streamlit as st
from advisor import search_funds # Ensure advisor.py is in the main directory


import streamlit as st
import base64

# --- Function to get base64 encoded image ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Path to your background image ---
# IMPORTANT: Change this to your actual image path for THIS specific page!
# If you want the SAME image on all pages, ensure this path is consistent across all pages.
background_image_path = "black-particles-background.avif" # Example path

# --- Get the base64 encoded string and inject CSS ---
try:
    encoded_image = get_base64_image(background_image_path)
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{encoded_image}");
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

st.title("🔍 Mutual Fund Research")

st.set_page_config(page_title="Mutual Fund Research", page_icon="🔍", layout="wide")

st.write("Explore and compare various mutual funds to find the best fit for your portfolio. Search by fund name, category, or performance metrics to gain insights into historical returns, expenses, and holdings.")
# ... rest of your page code ...
st.markdown("<p style='font-size: 1.1rem;'>Search for mutual funds by name to get details.</p>", unsafe_allow_html=True)

search_query = st.text_input("Enter fund name to search", key="mfr_fund_search_input") # Unique key

if search_query:
    funds = search_funds(search_query)
    found_funds_info = []
    if funds:
        st.subheader("Top 5 Search Results:")
        for fund in funds[:5]:
            st.markdown(f"<p style='color: white;'><b>{fund['schemeName']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: white;'>Scheme Code: {fund.get('schemeCode', 'N/A')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: white;'>[Live NAV](https://api.mfapi.in/mf/{fund.get('schemeCode', '')})</p>", unsafe_allow_html=True)
            st.markdown("---")
            found_funds_info.append(f"{fund['schemeName']} (Code: {fund.get('schemeCode', 'N/A')})")
        # --- Capture for AI Summary ---
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        st.session_state['ai_summary_data']['Mutual Fund Research'] = {
            "query": search_query,
            "results": f"Found {len(funds)} funds. Top 5: {', '.join(found_funds_info)}"
        }
    else:
        st.markdown("<p style='color: white;'>No funds found for your query.</p>", unsafe_allow_html=True)
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        st.session_state['ai_summary_data']['Mutual Fund Research'] = {
            "query": search_query,
            "results": "No funds found."
        }
st.markdown("---")
