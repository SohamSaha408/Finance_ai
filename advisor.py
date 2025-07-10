# advisor.py
import google.generativeai as genai
import requests
import streamlit as st # To access st.secrets

def generate_recommendation(age, income, profession, region, goal):
    """Generates investment recommendation using Gemini AI."""
    try:
        genai.configure(api_key=st.secrets["gemini"]["api_key"])
    except KeyError:
        return {"advice_text": "Error: Gemini API key not found in Streamlit secrets.", "allocation": {"Equity": "₹0", "Debt": "₹0", "Gold": "₹0"}}

    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = (
        f"As an expert Indian financial advisor, provide a detailed investment recommendation for a client "
        f"with the following profile:\n\n"
        f"Age: {age}\n"
        f"Monthly Income: ₹{income:,}\n"
        f"Profession: {profession}\n"
        f"Region: {region}\n"
        f"Investment Goal: {goal}\n\n"
        f"Please include:\n"
        f"1. A concise investment advice summary (2-3 paragraphs).\n"
        f"2. A suggested asset allocation in percentages (Equity, Debt, Gold). Express as absolute INR amounts for a hypothetical investment of 100,000 to clearly show the breakdown. Example: Equity: ₹60,000, Debt: ₹30,000, Gold: ₹10,000.\n"
        f"3. General guidance on suitable investment products for India, based on the allocation (e.g., specific types of mutual funds, government bonds, digital gold).\n"
        f"Format your response clearly, with headings for Advice, Allocation, and Product Guidance."
    )
    try:
        response = model.generate_content(contents=[{"role": "user", "parts": [prompt]}])
        advice_text = response.text

        # Extracting allocation from the AI's response (simplified regex for example)
        # You might need to refine this regex based on actual AI output format
        equity_match = re.search(r"Equity:\s*(₹[\d,]+)", advice_text)
        debt_match = re.search(r"Debt:\s*(₹[\d,]+)", advice_text)
        gold_match = re.search(r"Gold:\s*(₹[\d,]+)", advice_text)

        allocation = {
            "Equity": equity_match.group(1) if equity_match else "₹0",
            "Debt": debt_match.group(1) if debt_match else "₹0",
            "Gold": gold_match.group(1) if gold_match else "₹0"
        }

        return {"advice_text": advice_text, "allocation": allocation}
    except Exception as e:
        return {"advice_text": f"Error generating recommendation: {e}. Please check your API key or try again.", "allocation": {"Equity": "₹0", "Debt": "₹0", "Gold": "₹0"}}

def search_funds(query):
    """Searches for mutual funds using mfapi.in API."""
    url = f"https://api.mfapi.in/mf/search?q={query}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching mutual funds: {e}. Please check your internet connection or the API service.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred during fund search: {e}")
        return []
