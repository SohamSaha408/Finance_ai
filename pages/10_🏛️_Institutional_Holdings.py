import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from utils.styling import set_common_font # Adjust path if your utils folder is structured differently
# --- Page Configuration ---
st.set_page_config(page_title="Institutional Holdings", page_icon="🏛️", layout="wide")

st.title("🏛️ Institutional Holdings (Form 13F Filings)")
st.markdown("""
    <p style='font-size: 1.1rem;'>
        Discover what major institutional investors are buying and selling.
        This data is sourced from quarterly Form 13F filings with the SEC.
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

# --- Function to fetch recent 13F filings for an institutional manager (CIK) ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def fetch_13f_filings(cik, num_filings_to_check=5):
    """
    Fetches recent Form 13F filings for a given institutional manager CIK.
    Note: Extracting the actual holdings data from within the 13F form (often XML)
    is complex and not directly supported by the /submissions API.
    This function primarily finds the filings and their links.
    """
    cik_padded = str(cik).zfill(10)
    url = f"{SEC_SUBMISSIONS_API_BASE_URL}/CIK{cik_padded}.json"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        form_13f_filings = []
        if 'filings' in data and 'recent' in data['filings']:
            forms = data['filings']['recent']['form']
            filing_dates = data['filings']['recent']['filingDate']
            report_dates = data['filings']['recent']['reportDate']
            accession_numbers = data['filings']['recent']['accessionNumber']
            primary_docs = data['filings']['recent']['primaryDocument']
            
            count = 0
            for i in range(len(forms)):
                if forms[i] in ['13F-HR', '13F-HT', '13F-CR', '13F-NT']: # Look for 13F variants
                    if count >= num_filings_to_check:
                        break
                    
                    accession_no_cleaned = accession_numbers[i].replace('-', '')
                    filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_padded}/{accession_no_cleaned}/{primary_docs[i]}"

                    form_13f_filings.append({
                        "Form Type": forms[i],
                        "Filing Date": filing_dates[i],
                        "Report Date": report_dates[i],
                        "Link": filing_url
                    })
                    count += 1
        return form_13f_filings
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching 13F filings for CIK {cik}: {e}. Ensure the CIK is correct and User-Agent set.")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return []

# --- Main Page Content ---
st.header("Search for an Institutional Investor's 13F Filings")
st.info("Tip: Search for well-known institutional investors like 'Berkshire Hathaway Inc' or 'BlackRock Inc'. You'll need the CIK of the *institution*, not the company they invest in.")

# Note: The CIK map primarily contains company CIKs. For 13F, you need manager CIKs.
# We'll use a hardcoded example for Berkshire Hathaway as a large 13F filer.
# For other managers, users would typically need to find the CIK manually or via a separate lookup.
manager_input_name = st.text_input("Enter Institutional Investor Name (e.g., Berkshire Hathaway Inc, BlackRock Inc):", key="manager_search_input")

# Simplified CIK lookup for managers - extend as needed
manager_cik_map = {
    "BERKSHIRE HATHAWAY INC": "0000010679",
    "BLACKROCK INC": "0001364742",
    "VANGUARD GROUP INC": "0001029093",
    "STATE STREET CORP": "0000093751",
    # Add more institutional investor CIKs as needed
}

manager_cik = None
if manager_input_name:
    normalized_manager_name = manager_input_name.upper().strip()
    manager_cik = manager_cik_map.get(normalized_manager_name, None)

if manager_input_name and manager_cik:
    st.success(f"Found CIK for {manager_input_name}: **{manager_cik}**")
    with st.spinner(f"Fetching recent 13F filings for {manager_input_name} (CIK: {manager_cik})..."):
        filings_data = fetch_13f_filings(manager_cik)
    
    if filings_data:
        df_filings = pd.DataFrame(filings_data)
        df_filings['Filing Date'] = pd.to_datetime(df_filings['Filing Date'])
        df_filings = df_filings.sort_values(by='Filing Date', ascending=False)
        
        st.subheader(f"Recent 13F Filings for {manager_input_name}")
        
        display_df = df_filings.copy()
        display_df['Link'] = display_df['Link'].apply(lambda x: f"[View Filing]({x})")
        
        st.markdown(display_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        
        st.info("""
            **Understanding 13F Filings:**
            * **Form 13F-HR**: The most common type, details all holdings at the end of the quarter.
            * **Form 13F-HT**: Notice of a confidential portion of a 13F-HR.
            * **Form 13F-CR**: Confidential request for a 13F-HR.
            * **Form 13F-NT**: Notice of intention not to file a 13F.

            **Note:** This table provides links to the 13F filings. **To view the actual stock holdings (which companies and how many shares), you must click on the "View Filing" link and navigate within the filing to the "informationTable" section (often an XML file).** Extracting these specific holdings details programmatically is complex and usually requires a dedicated XBRL/XML parsing library or a specialized API service.
        """)

        # Optional: Update session state for AI summary
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        st.session_state['ai_summary_data']['Institutional Holdings'] = {
            "manager_name": manager_input_name,
            "manager_cik": manager_cik,
            "num_filings": len(filings_data),
            "status": "13F filings displayed successfully."
        }
    else:
        st.warning(f"No recent 13F filings found for {manager_input_name} (CIK: {manager_cik}), or an error occurred during fetch.")
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        st.session_state['ai_summary_data']['Institutional Holdings'] = {
            "manager_name": manager_input_name,
            "manager_cik": manager_cik,
            "num_filings": 0,
            "status": "No 13F filings or error."
        }
elif manager_input_name and not manager_cik:
    st.warning(f"Could not find CIK for '{manager_input_name}'. Please try a different name or provide the exact CIK.")
else:
    st.info("Enter an institutional investor's name above to search for their latest 13F filings.")

st.markdown("---")
