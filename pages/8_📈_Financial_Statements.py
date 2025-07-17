import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Financial Statements", page_icon="📈", layout="wide")

st.title("📈 Company Financial Statements")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Access and analyze key financial statements (Income Statement, Balance Sheet, Cash Flow)
        for public companies directly from SEC EDGAR filings (10-K & 10-Q).
    </p>
    """, unsafe_allow_html=True)

# --- SEC EDGAR API Base URL for Company Facts ---
SEC_COMPANY_FACTS_BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts"

# --- REQUIRED: Set a proper User-Agent header ---
# Remember to replace "YourAppName" and "YourContactEmail" with your actual details.
HEADERS = {
    'User-Agent': 'YourAppName/1.0 YourContactEmail@example.com' # <--- IMPORTANT: Update this!
}

# --- CIK Lookup (Simplified - Same as Financial News page) ---
# In a full application, you would use a more robust CIK lookup service or a downloaded mapping.
@st.cache_data(ttl=86400) # Cache for 24 hours
def get_cik_from_company_name_rough(company_name):
    company_cik_map = {
        "APPLE INC": "0000320193",
        "MICROSOFT CORP": "0000789019",
        "AMAZON COM INC": "0001018724",
        "TESLA INC": "0001318605",
        "NVIDIA CORP": "0001045810",
        "GOOGLE": "0001652044", # Alphabet Inc.
        "ALPHABET INC": "0001652044",
        "BERKSHIRE HATHAWAY INC": "0000010679",
        "SALESFORCE INC": "0001108524" # Added for testing
    }
    normalized_name = company_name.upper().strip()
    return company_cik_map.get(normalized_name, None)

# --- Function to fetch company facts ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_company_facts(cik):
    """Fetches company facts data (XBRL) for a given CIK."""
    # Ensure CIK is 10 digits padded with leading zeros
    cik_padded = str(cik).zfill(10)
    url = f"{SEC_COMPANY_FACTS_BASE_URL}/CIK{cik_padded}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching company facts for CIK {cik}: {e}. Please ensure the CIK is correct and your User-Agent is set.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Helper to extract and process financial data for a concept ---
def extract_financial_data(facts_data, concept_type, concept_name, unit='USD', label=None):
    """
    Extracts financial data for a given concept from the company facts data.
    Organizes it by end date and value.
    """
    if facts_data and concept_type in facts_data.get('facts', {}) and concept_name in facts_data['facts'][concept_type]:
        concept_data = facts_data['facts'][concept_type][concept_name]['units'].get(unit)
        if concept_data:
            df = pd.DataFrame(concept_data)
            df['end'] = pd.to_datetime(df['end'])
            df['val'] = pd.to_numeric(df['val'], errors='coerce')
            df = df.dropna(subset=['val'])
            df = df[['end', 'val']].sort_values(by='end', ascending=False).drop_duplicates(subset='end')
            df.columns = ['Date', label if label else concept_name]
            return df
    return pd.DataFrame(columns=['Date', label if label else concept_name])

# --- Main Page Content ---
st.header("Search for a Company's Financial Statements")

company_input = st.text_input("Enter Company Name (e.g., Apple Inc, Microsoft Corp):", key="fs_company_search_input")

if company_input:
    cik = get_cik_from_company_name_rough(company_input)
    
    if cik:
        st.success(f"Found CIK for {company_input}: **{cik}**")
        with st.spinner(f"Fetching financial statements for {company_input} (CIK: {cik})..."):
            facts = fetch_company_facts(cik)
        
        if facts:
            st.subheader(f"Financial Statements for {company_input}")

            # --- Income Statement ---
            st.markdown("### Income Statement (Consolidated)")
            revenue_df = extract_financial_data(facts, 'us-gaap', 'Revenues', label='Revenues')
            net_income_df = extract_financial_data(facts, 'us-gaap', 'NetIncomeLoss', label='Net Income Loss')
            
            if not revenue_df.empty and not net_income_df.empty:
                income_statement_df = pd.merge(revenue_df, net_income_df, on='Date', how='outer')
                income_statement_df = income_statement_df.sort_values(by='Date', ascending=False)
                st.dataframe(income_statement_df.set_index('Date').head(10)) # Show latest 10
            elif not revenue_df.empty:
                st.dataframe(revenue_df.set_index('Date').head(10))
            elif not net_income_df.empty:
                st.dataframe(net_income_df.set_index('Date').head(10))
            else:
                st.info("No readily available Income Statement data found for these key concepts.")

            st.markdown("---")

            # --- Balance Sheet ---
            st.markdown("### Balance Sheet (Consolidated)")
            assets_df = extract_financial_data(facts, 'us-gaap', 'Assets', label='Total Assets')
            liabilities_df = extract_financial_data(facts, 'us-gaap', 'Liabilities', label='Total Liabilities')
            equity_df = extract_financial_data(facts, 'us-gaap', 'StockholdersEquity', label='Total Equity')

            if not assets_df.empty or not liabilities_df.empty or not equity_df.empty:
                balance_sheet_df = pd.merge(assets_df, liabilities_df, on='Date', how='outer')
                balance_sheet_df = pd.merge(balance_sheet_df, equity_df, on='Date', how='outer')
                balance_sheet_df = balance_sheet_df.sort_values(by='Date', ascending=False)
                st.dataframe(balance_sheet_df.set_index('Date').head(10)) # Show latest 10
            else:
                st.info("No readily available Balance Sheet data found for these key concepts.")
            
            st.markdown("---")

            # --- Cash Flow Statement ---
            st.markdown("### Cash Flow Statement (Consolidated)")
            operating_cash_flow_df = extract_financial_data(facts, 'us-gaap', 'NetCashProvidedByUsedInOperatingActivities', label='Operating Cash Flow')
            investing_cash_flow_df = extract_financial_data(facts, 'us-gaap', 'NetCashProvidedByUsedInInvestingActivities', label='Investing Cash Flow')
            financing_cash_flow_df = extract_financial_data(facts, 'us-gaap', 'NetCashProvidedByUsedInFinancingActivities', label='Financing Cash Flow')
            
            if not operating_cash_flow_df.empty or not investing_cash_flow_df.empty or not financing_cash_flow_df.empty:
                cash_flow_df = pd.merge(operating_cash_flow_df, investing_cash_flow_df, on='Date', how='outer')
                cash_flow_df = pd.merge(cash_flow_df, financing_cash_flow_df, on='Date', how='outer')
                cash_flow_df = cash_flow_df.sort_values(by='Date', ascending=False)
                st.dataframe(cash_flow_df.set_index('Date').head(10)) # Show latest 10
            else:
                st.info("No readily available Cash Flow Statement data found for these key concepts.")
            
            st.markdown("---")

            st.info("Note: Data is sourced from SEC EDGAR XBRL company facts. Not all concepts may be available for all companies or periods.")

            # Optional: Update session state for AI summary
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Financial Statements'] = {
                "company": company_input,
                "cik": cik,
                "status": "Financial statements displayed successfully."
            }

        else:
            st.warning(f"Could not retrieve company facts for {company_input} (CIK: {cik}). This could be due to an invalid CIK, no data available, or an API error.")
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Financial Statements'] = {
                "company": company_input,
                "cik": cik,
                "status": "No facts or error."
            }
    else:
        st.warning(f"Could not find CIK for '{company_input}'. Please try a different company name or provide the exact CIK.")
else:
    st.info("Enter a company name above to view its latest financial statements.")

st.markdown("---")
