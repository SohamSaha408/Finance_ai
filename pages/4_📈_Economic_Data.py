import streamlit as st
import pandas as pd
from fredapi import Fred # Make sure fredapi is installed (pip install fredapi)

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

st.title("📈 Economic Data from FRED")
st.markdown("<p style='font-size: 1.1rem;'>Enter a FRED Series ID (e.g., `UNRATE` for Unemployment Rate, `GDP` for Gross Domestic Product) to view economic data.</p>", unsafe_allow_html=True)

fred_series_id = st.text_input(
    "FRED Series ID:",
    value="UNRATE", # Default example
    key="fred_series_input" # Unique key
).strip().upper()

def get_fred_data(series_id, start_date=None, end_date=None):
    try:
        fred_api_key = st.secrets["fred"]["api_key"]
        fred = Fred(api_key=fred_api_key)
        data = fred.get_series(series_id, observation_start=start_date, observation_end=end_date)
        if data is not None and not data.empty:
            df = pd.DataFrame(data)
            df.columns = [series_id]
            df.index.name = 'Date'
            return df
        else:
            st.warning(f"No data found for FRED Series ID: `{series_id}`. Please check the ID.")
            return None
    except KeyError:
        st.error("FRED API key not found in Streamlit secrets. Please set it as `fred.api_key` in .streamlit/secrets.toml or Streamlit Cloud secrets.")
        return None
    except Exception as e:
        st.error(f"An error occurred while fetching FRED data: {e}")
        return None

if st.button("Get FRED Data", key="fred_fetch_data_btn"): # Unique key
    if fred_series_id:
        with st.spinner(f"Fetching data for {fred_series_id} from FRED..."):
            fred_df = get_fred_data(fred_series_id)

            if fred_df is not None:
                st.subheader(f"Latest Data for {fred_series_id}")
                st.dataframe(fred_df.tail())

                # --- Capture for AI Summary ---
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['FRED Data'] = {
                    "series_id": fred_series_id,
                    "data_summary": f"Latest 5 observations for {fred_series_id}:\n" + fred_df.tail().to_markdown()
                }
            else:
                st.info("No data could be retrieved for the provided FRED Series ID.")
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['FRED Data'] = {
                    "series_id": fred_series_id,
                    "data_summary": "No data retrieved."
                }
    else:
        st.warning("Please enter a FRED Series ID to fetch data.")
st.markdown("---")
