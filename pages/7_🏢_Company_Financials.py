import streamlit as st
import pandas as pd
import requests # Make sure requests is installed

st.title("🏢 Company Financials (via Alpha Vantage)")
st.markdown("<p style='font-size: 1.1rem;'>Get key financial statements (e.g., Income Statement) for publicly traded companies using their ticker symbol.</p>", unsafe_allow_html=True)

company_ticker_av = st.text_input(
    "Enter Company Stock Ticker (e.g., IBM, GOOGL, MSFT):",
    key="cf_company_ticker_av_input" # Unique key
).strip().upper()

statement_type_selected = st.selectbox(
    "Select Statement Type:",
    options=["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"],
    key="cf_statement_type_select" # Unique key
)

def get_company_financials(symbol, statement_type="INCOME_STATEMENT"):
    try:
        av_api_key = st.secrets["alphavantage"]["api_key"]
        url = f"https://www.alphavantage.co/query?function={statement_type}&symbol={symbol}&apikey={av_api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "annualReports" in data:
            st.subheader(f"Annual {statement_type.replace('_', ' ').title()} for {symbol}")
            df = pd.DataFrame(data["annualReports"])
            numeric_cols = [col for col in df.columns if col not in ['fiscalDateEnding', 'reportedCurrency']]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            desired_order = ['fiscalDateEnding', 'reportedCurrency', 'totalRevenue', 'netIncome', 'earningsPerShare', 'totalShareholderEquity']
            ordered_cols = [col for col in desired_order if col in df.columns] + \
                           [col for col in df.columns if col not in desired_order]
            df = df[ordered_cols]

            st.dataframe(df.set_index('fiscalDateEnding'))
            return df
        elif "Note" in data:
            st.warning(f"Alpha Vantage API note for {symbol}: {data['Note']}. This often indicates a rate limit, an invalid symbol, or no data for the requested function.")
        else:
            st.warning(f"No {statement_type.replace('_', ' ').lower()} data found for {symbol}. Check the symbol or API key.")
        return None
    except KeyError:
        st.error("Alpha Vantage API key not found in Streamlit secrets. Please add `alphavantage.api_key` to .streamlit/secrets.toml or Streamlit Cloud secrets.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching financial statements for {symbol}: {e}. Check API key or internet connection.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching financial statements: {e}")
        return None

if st.button("Get Company Financials", key="cf_get_company_financials_btn"): # Unique key
    if company_ticker_av:
        with st.spinner(f"Fetching {statement_type_selected.replace('_', ' ').lower()} for {company_ticker_av}..."):
            company_df = get_company_financials(company_ticker_av, statement_type=statement_type_selected)
            if company_df is not None:
                # --- Capture for AI Summary ---
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Company Financials'] = {
                    "ticker": company_ticker_av,
                    "statement_type": statement_type_selected,
                    "financial_data_head": company_df.head().to_markdown()
                }
            else:
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Company Financials'] = {
                    "ticker": company_ticker_av,
                    "statement_type": statement_type_selected,
                    "financial_data_head": "No data found."
                }
    else:
        st.warning("Please enter a company stock ticker.")
st.markdown("---")
