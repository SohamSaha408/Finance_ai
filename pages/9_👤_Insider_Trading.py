import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Insider Trading", page_icon="👤", layout="wide")

st.title("👤 Insider Trading Activity")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        View recent insider trading activities (Form 3, 4, and 5 filings) for public companies.
        Insider transactions can provide unique insights into a company's prospects.
    </p>
    """, unsafe_allow_html=True)

# --- SEC EDGAR API Base URL for Submissions (used to find filings) ---
SEC_SUBMISSIONS_API_BASE_URL = "https://data.sec.gov/submissions"

# --- REQUIRED: Set a proper User-Agent header ---
# Remember to replace "YourAppName" and "YourContactEmail" with your actual details.
HEADERS = {
    'User-Agent': 'YourAppName/1.0 YourContactEmail@example.com' # <--- IMPORTANT: Update this!
}

# --- CIK Lookup (Simplified - Same as other pages) ---
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
        "SALESFORCE INC": "0001108524"
    }
    normalized_name = company_name.upper().strip()
    return company_cik_map.get(normalized_name, None)

# --- Function to fetch insider transaction filings (Form 3, 4, 5) ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_insider_filings(cik, num_filings_to_check=50):
    """
    Fetches recent Form 3, 4, and 5 filings for a given CIK.
    Note: Parsing the actual transaction data from these forms requires
    more complex XBRL parsing or a dedicated API/library.
    This function primarily finds the filings and their links.
    """
    cik_padded = str(cik).zfill(10)
    url = f"{SEC_SUBMISSIONS_API_BASE_URL}/CIK{cik_padded}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        insider_filings = []
        if 'filings' in data and 'recent' in data['filings']:
            forms = data['filings']['recent']['form']
            filing_dates = data['filings']['recent']['filingDate']
            report_dates = data['filings']['recent']['reportDate']
            accession_numbers = data['filings']['recent']['accessionNumber']
            primary_docs = data['filings']['recent']['primaryDocument']
            
            count = 0
            for i in range(len(forms)):
                if forms[i] in ['3', '4', '5']: # Look for insider trading forms
                    if count >= num_filings_to_check: # Limit the number of filings to check
                        break
                    
                    accession_no_cleaned = accession_numbers[i].replace('-', '')
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession_no_cleaned}/{primary_docs[i]}"

                    insider_filings.append({
                        "Form Type": forms[i],
                        "Filing Date": filing_dates[i],
                        "Report Date": report_dates[i],
                        "Link": filing_url
                    })
                    count += 1
        return insider_filings
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching insider filings for CIK {cik}: {e}. Ensure the CIK is correct and User-Agent set.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

# --- Main Page Content ---
st.header("Search for a Company's Insider Trading Activity")

company_input = st.text_input("Enter Company Name (e.g., Tesla Inc, Apple Inc):", key="insider_company_search_input")

if company_input:
    cik = get_cik_from_company_name_rough(company_input)
    
    if cik:
        st.success(f"Found CIK for {company_input}: **{cik}**")
        with st.spinner(f"Fetching recent insider filings for {company_input} (CIK: {cik})..."):
            filings_data = fetch_insider_filings(cik)
        
        if filings_data:
            df_filings = pd.DataFrame(filings_data)
            
            # Convert 'Filing Date' to datetime objects for sorting
            df_filings['Filing Date'] = pd.to_datetime(df_filings['Filing Date'])
            df_filings = df_filings.sort_values(by='Filing Date', ascending=False)
            
            st.subheader(f"Recent Insider Filings for {company_input}")
            
            # Display filings with clickable links
            display_df = df_filings.copy()
            display_df['Link'] = display_df['Link'].apply(lambda x: f"[View Filing]({x})")
            
            st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            st.info("""
                Note: This table provides links to Form 3, 4, and 5 filings.
                To view transaction details (e.g., shares bought/sold, price), you need to click
                on the "View Filing" link and examine the filing's content. Extracting these
                specific transaction details programmatically is more complex and typically
                requires dedicated XBRL parsing libraries or services.
            """)

            # Optional: Update session state for AI summary
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Insider Trading'] = {
                "company": company_input,
                "cik": cik,
                "num_filings": len(filings_data),
                "status": "Insider filings displayed successfully."
            }
        else:
            st.warning(f"No recent Form 3, 4, or 5 filings found for {company_input} (CIK: {cik}) in the latest {num_filings_to_check} filings, or an error occurred during fetch.")
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Insider Trading'] = {
                "company": company_input,
                "cik": cik,
                "num_filings": 0,
                "status": "No insider filings or error."
            }
    else:
        st.warning(f"Could not find CIK for '{company_input}'. Please try a different company name or provide the exact CIK.")
else:
    st.info("Enter a company name above to search for its latest insider trading activities.")

st.markdown("---")
