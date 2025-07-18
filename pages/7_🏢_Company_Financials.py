import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai
import numpy as np # For checking NaN values

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

# --- Streamlit Page Config ---
st.set_page_config(page_title="Company Financials", page_icon="🏢")



st.set_page_config(page_title="Company Financials", page_icon="📈", layout="wide")
st.title("📈 Company Financials")
st.write("Dive deep into a company's financial health. Access historical income statements, balance sheets, and cash flow statements to perform fundamental analysis and assess performance.")
# ... rest of your page code ...
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Get key financial statements (e.g., Income Statement) for publicly traded companies using their ticker symbol.
    </p>
    """, unsafe_allow_html=True)

# --- Configure Gemini API (moved to top for efficiency) ---
try:
    genai.configure(api_key=st.secrets["gemini"]["api_key"])
    model = genai.GenerativeModel("gemini-1.5-flash")
except KeyError:
    st.error("Gemini API key not found in secrets. Add `gemini.api_key` to `.streamlit/secrets.toml`.")
    st.stop() # Stop execution if API key is missing
except Exception as e:
    st.error(f"Error configuring Gemini API: {e}")
    st.stop()

# --- User Inputs ---
company_ticker_av = st.text_input(
    "Enter Company Stock Ticker (e.g., IBM, GOOGL, MSFT):",
    key="cf_company_ticker_av_input"
).strip().upper()

statement_type_selected = st.selectbox(
    "Select Statement Type:",
    options=["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"],
    key="cf_statement_type_select"
)

# New: Select between Annual and Quarterly Reports
report_period_selected = st.radio(
    "Select Report Period:",
    options=["Annual", "Quarterly"],
    key="cf_report_period_select",
    horizontal=True
)

# --- Define Function to Get Financials ---
def get_company_financials(symbol, statement_type, report_period):
    try:
        av_api_key = st.secrets["alphavantage"]["api_key"]
        url = f"https://www.alphavantage.co/query?function={statement_type}&symbol={symbol}&apikey={av_api_key}"
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        data_key = "annualReports" if report_period == "Annual" else "quarterlyReports"

        if data_key in data and data[data_key]: # Check if key exists AND list is not empty
            st.subheader(f"📄 {report_period} {statement_type.replace('_', ' ').title()} for {symbol}")
            df = pd.DataFrame(data[data_key])

            # Convert all relevant columns to numeric, coercing errors to NaN
            for col in df.columns:
                if col not in ['fiscalDateEnding', 'reportedCurrency']: # Exclude non-numeric columns
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Define desired order based on statement type for better readability
            if statement_type == "INCOME_STATEMENT":
                desired_order = ['fiscalDateEnding', 'reportedCurrency', 'totalRevenue', 'netIncome',
                                 'grossProfit', 'ebitda', 'earningsPerShare']
            elif statement_type == "BALANCE_SHEET":
                desired_order = ['fiscalDateEnding', 'reportedCurrency', 'totalAssets', 'totalLiabilities',
                                 'totalShareholderEquity', 'cashAndCashEquivalentsAtCarryingValue']
            elif statement_type == "CASH_FLOW":
                desired_order = ['fiscalDateEnding', 'reportedCurrency', 'operatingCashflow', 'investingCashflow',
                                 'financingCashflow', 'freeCashflow']
            else:
                desired_order = ['fiscalDateEnding', 'reportedCurrency'] # Fallback

            # Reorder columns: relevant first, then any others
            ordered_cols = [col for col in desired_order if col in df.columns] + \
                           [col for col in df.columns if col not in desired_order and col not in ['fiscalDateEnding', 'reportedCurrency']]
            df = df[ordered_cols]

            st.dataframe(df.set_index('fiscalDateEnding'))
            return df
        elif "Note" in data:
            st.warning(f"Alpha Vantage API note for {symbol}: {data['Note']}. This may indicate rate limiting or invalid request.")
        else:
            st.warning(f"No {report_period.lower()} {statement_type.replace('_', ' ').lower()} data found for {symbol}.")
        return None

    except KeyError:
        st.error("Alpha Vantage API key not found in secrets. Add `alphavantage.api_key` to `.streamlit/secrets.toml`.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching financials for {symbol}: {e}. Please check your internet connection or the ticker symbol.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred in `get_company_financials`: {e}")
        return None

# --- Main Execution ---
if st.button("Get Company Financials", key="cf_get_company_financials_btn"):
    if not company_ticker_av:
        st.warning("Please enter a company ticker symbol.")
        st.session_state['ai_summary_data'] = {'Company Financials': {'status': 'No ticker entered'}}
        st.stop() # Stop further execution

    with st.spinner(f"Fetching {report_period_selected.lower()} {statement_type_selected.replace('_', ' ').lower()} for {company_ticker_av}..."):
        company_df = get_company_financials(company_ticker_av,
                                            statement_type=statement_type_selected,
                                            report_period=report_period_selected)

        if company_df is not None and not company_df.empty: # Ensure DataFrame is not None and not empty
            # --- AI Review Integration ---
            try:
                # Use iloc[0] for the most recent report (Alpha Vantage usually returns most recent first)
                latest_report = company_df.iloc[0]

                # Dynamically build summary text with robust NaN handling for AI prompt
                summary_parts = []
                summary_parts.append(f"Latest {report_period_selected} {statement_type_selected.replace('_', ' ').title()} for {company_ticker_av}:")
                summary_parts.append(f"- Fiscal Date Ending: {latest_report.get('fiscalDateEnding', 'N/A')}")
                summary_parts.append(f"- Reported Currency: {latest_report.get('reportedCurrency', 'N/A')}")

                # Iterate through all columns in the latest report, format numeric and handle NaN
                for col_name, value in latest_report.items():
                    if col_name not in ['fiscalDateEnding', 'reportedCurrency']:
                        if pd.api.types.is_numeric_dtype(type(value)):
                            formatted_value = f"{value:,.2f}" if not pd.isna(value) else 'N/A'
                        else:
                            formatted_value = str(value) if value is not None else 'N/A'
                        summary_parts.append(f"- {col_name.replace('_', ' ').title()}: {formatted_value}")

                summary_text = "\n".join(summary_parts)

                prompt = f"""
                Analyze the following financial summary for {company_ticker_av} and generate a concise, investor-focused review.
                Highlight key figures and any notable trends or observations.

                {summary_text}
                """

                with st.spinner("Generating AI review..."):
                    ai_response = model.generate_content(prompt)

                st.subheader("🧠 AI Review")
                st.markdown(ai_response.text)

                # Save to session state for AI Summary page
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Company Financials'] = {
                    "ticker": company_ticker_av,
                    "statement_type": statement_type_selected,
                    "report_period": report_period_selected,
                    "financial_data_head": company_df.head().to_markdown(), # Store a markdown version
                    "ai_review": ai_response.text
                }

            except Exception as e:
                st.warning(f"AI review generation failed: {e}. Please ensure relevant data is available and Gemini API is correctly configured.")
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Company Financials'] = {
                    "ticker": company_ticker_av,
                    "statement_type": statement_type_selected,
                    "report_period": report_period_selected,
                    "financial_data_head": "N/A",
                    "ai_review": f"AI generation error: {e}"
                }

        else:
            st.info("No financial data was returned or the data received was empty after processing.")
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Company Financials'] = {
                "ticker": company_ticker_av,
                "statement_type": statement_type_selected,
                "report_period": report_period_selected,
                "financial_data_head": "N/A",
                "ai_review": "No data available for AI review."
            }
else:
    st.info("Enter a company ticker symbol and select the statement type, then click 'Get Company Financials'.")

st.markdown("---") # Visual separator at the bottom
