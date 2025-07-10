import streamlit as st
import pandas as pd
import re # Make sure re is imported if you use it in extract_amount
from advisor import generate_recommendation # Ensure advisor.py is in the main directory

st.title("📊 Your Personalized Investment Plan")

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
