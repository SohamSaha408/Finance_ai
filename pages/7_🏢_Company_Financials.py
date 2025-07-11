import streamlit as st
import pandas as pd
import requests
import google.generativeai as genai

# --- Streamlit Page Config ---
st.set_page_config(page_title="Company Financials", page_icon="🏢")

st.title("🏢 Company Financials (via Alpha Vantage)")
st.markdown("<p style='font-size: 1.1rem;'>Get key financial statements (e.g., Income Statement) for publicly traded companies using their ticker symbol.</p>", unsafe_allow_html=True)

# --- User Input ---
company_ticker_av = st.text_input(
    "Enter Company Stock Ticker (e.g., IBM, GOOGL, MSFT):",
    key="cf_company_ticker_av_input"
).strip().upper()

statement_type_selected = st.selectbox(
    "Select Statement Type:",
    options=["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"],
    key="cf_statement_type_select"
)

# --- Define Function to Get Financials ---
def get_company_financials(symbol, statement_type="INCOME_STATEMENT"):
    try:
        av_api_key = st.secrets["alphavantage"]["api_key"]
        url = f"https://www.alphavantage.co/query?function={statement_type}&symbol={symbol}&apikey={av_api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "annualReports" in data:
            st.subheader(f"📄 Annual {statement_type.replace('_', ' ').title()} for {symbol}")
            df = pd.DataFrame(data["annualReports"])
            numeric_cols = [col for col in df.columns if col not in ['fiscalDateEnding', 'reportedCurrency']]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Reorder columns for clarity
            desired_order = ['fiscalDateEnding', 'reportedCurrency', 'totalRevenue', 'netIncome',
                             'earningsPerShare', 'totalShareholderEquity']
            ordered_cols = [col for col in desired_order if col in df.columns] + \
                           [col for col in df.columns if col not in desired_order]
            df = df[ordered_cols]

            st.dataframe(df.set_index('fiscalDateEnding'))
            return df
        elif "Note" in data:
            st.warning(f"Alpha Vantage API note for {symbol}: {data['Note']}. This may indicate rate limiting.")
        else:
            st.warning(f"No {statement_type.replace('_', ' ').lower()} data found for {symbol}.")
        return None

    except KeyError:
        st.error("Alpha Vantage API key not found in secrets. Add `alphavantage.api_key` to `.streamlit/secrets.toml`.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching financials for {symbol}: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error while fetching financials: {e}")
        return None

# --- Main Execution ---
if st.button("Get Company Financials", key="cf_get_company_financials_btn"):
    if company_ticker_av:
        with st.spinner(f"Fetching {statement_type_selected.replace('_', ' ').lower()} for {company_ticker_av}..."):
            company_df = get_company_financials(company_ticker_av, statement_type=statement_type_selected)

            if company_df is not None:
                # --- AI Review Integration ---
                try:
                    genai.configure(api_key=st.secrets["gemini"]["api_key"])
                    model = genai.GenerativeModel("gemini-1.5-pro")

                    latest_report = company_df.iloc[0]
                    summary_text = f"""
                    Here's the latest annual {statement_type_selected.replace('_', ' ').title()} for {company_ticker_av}:
                    - Fiscal Year: {latest_report.get('fiscalDateEnding', 'N/A')}
                    - Total Revenue: {latest_report.get('totalRevenue', 'N/A')}
                    - Net Income: {latest_report.get('netIncome', 'N/A')}
                    - Earnings Per Share: {latest_report.get('earningsPerShare', 'N/A')}
                    - Shareholder Equity: {latest_report.get('totalShareholderEquity', 'N/A')}
                    """

                    prompt = f"""
                    Analyze the following financial summary and generate a concise review for an investor:

                    {summary_text}
                    """

                    with st.spinner("Generating AI review..."):
                        ai_response = model.generate_content(prompt)

                    st.subheader("🧠 AI Review")
                    st.markdown(ai_response.text)

                    # Save to session
                    if 'ai_summary_data' not in st.session_state:
                        st.session_state['ai_summary_data'] = {}
                    st.session_state['ai_summary_data']['Company Financials'] = {
                        "ticker": company_ticker_av,
                        "statement_type": statement_type_selected,
                        "financial_data_head": company_df.head().to_markdown(),
                        "ai_review": ai_response.text
                    }

                except Exception as e:
                    st.warning(f"AI review generation failed: {e}")

            else:
                st.info("No financial data was returned.")
    else:
        st.warning("Please enter a company ticker.")

