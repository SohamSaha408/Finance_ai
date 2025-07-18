import streamlit as st
import pandas as pd
import re # Make sure re is imported if you use it in extract_amount
from advisor import generate_recommendation # Ensure advisor.py is in the main directory

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

st.title("📊 Your Personalized Investment Plan")


st.markdown("---")
st.subheader("🤖 AI-Powered Review")

page_key_in_session_state = "Investment Plan"
display_name = "Investment Plan"

current_page_data = st.session_state.get('ai_summary_data', {}).get(page_key_in_session_state, {})

# You will need to define when your Investment Plan page considers data "available"
if current_page_data and current_page_data.get("status") == "Plan generated successfully.": # Example status, adjust as needed
    if st.button(f"Generate AI Review for {display_name}"):
        with st.spinner("Generating AI review..."):
            review = get_ai_review(display_name, current_page_data)
            st.write(review)
    else:
        st.info(f"Click the button above to get an AI-powered summary of the {display_name} data.")
else:
    st.info(f"No {display_name} data available to generate an AI review. Please generate an investment plan first.")

st.markdown("---")

st.markdown("<p style='font-size: 1.1rem;'>Answer a few questions to get tailored investment advice.</p>", unsafe_allow_html=True)

age = st.number_input("Age", min_value=18, key="ip_age_input") # Unique key
income = st.number_input("Monthly Income (₹)", step=1000, key="ip_income_input") # Unique key
profession = st.selectbox("Profession", ["Student", "Salaried", "Self-employed"], key="ip_prof_select") # Unique key
region = st.selectbox("Region", ["Metro", "Urban", "Rural"], key="ip_region_select") # Unique key
goal = st.selectbox("🎯 Investment Goal", [
    "Wealth Accumulation", "Retirement Planning", "Short-term Savings", "Tax Saving (ELSS)"
], key="ip_goal_select") # Unique key

def extract_amount(value_str):
    """Extracts numeric amount from a string like '₹12345'."""
    match = re.search(r"₹([0-9]+)", value_str)
    return int(match.group(1)) if match else 0

if st.button("Get Advice", key="ip_get_advice_btn"): # Unique key
    result = generate_recommendation(age, income, profession, region, goal)
    st.subheader("🧠 Advice")
    st.markdown(f"<p style='color: white;'>{result['advice_text']}</p>", unsafe_allow_html=True)

    st.subheader("📊 Allocation Data")
    alloc = result["allocation"]
    eq = extract_amount(alloc["Equity"])
    de = extract_amount(alloc["Debt"])
    go = extract_amount(alloc["Gold"])

    st.write(f"Equity: ₹{eq:,}")
    st.write(f"Debt: ₹{de:,}")
    st.write(f"Gold: ₹{go:,}")

    # --- Capture for AI Summary ---
    # Ensure st.session_state['ai_summary_data'] is initialized in Home.py
    if 'ai_summary_data' not in st.session_state:
        st.session_state['ai_summary_data'] = {} # Fallback
    st.session_state['ai_summary_data']['Investment Plan'] = {
        "user_inputs": f"Age: {age}, Income: {income}, Profession: {profession}, Region: {region}, Goal: {goal}",
        "advice": result['advice_text'],
        "allocation": f"Equity: {eq}, Debt: {de}, Gold: {go}"
    }

st.markdown("---")
