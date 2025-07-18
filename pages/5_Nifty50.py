import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(page_title="Nifty 50 Chart", page_icon="📈", layout="wide")

# --- Placeholder for get_cik_from_company_name_rough (if get_ai_review needs it or it's a shared utility) ---
@st.cache_data(ttl=86400) # Cache for 24 hours
def get_cik_from_company_name_rough(company_name):
    company_cik_map = {
        "APPLE INC": "0000320193", "MICROSOFT CORP": "0000789019",
        "AMAZON COM INC": "0001018724", "TESLA INC": "0001318605",
        "NVIDIA CORP": "0001045810", "GOOGLE": "0001652044", # Alphabet Inc.
        "ALPHABET INC": "0001652044", "BERKSHIRE HATHAWAY INC": "0000010679",
        "SALESFORCE INC": "0001108524"
    }
    normalized_name = company_name.upper().strip()
    return company_cik_map.get(normalized_name, None)

# --- get_ai_review Function ---
# IMPORTANT: Ensure you have configured your Google Gemini API key securely.
# Example: genai.configure(api_key=st.secrets["gemini"]["api_key"])
# Place your actual API key in .streamlit/secrets.toml file like this:
# [gemini]
# api_key = "YOUR_GEMINI_API_KEY"

@st.cache_data(ttl=300) # Cache AI responses for 5 minutes
def get_ai_review(page_name, page_data):
    """
    Generates an AI review/summary based on the provided page data.
    Replace the simulated AI response with your actual LLM integration.
    """
    if not page_data or page_data.get("status", "").startswith("Error") or page_data.get("chart_status", "").startswith("Error"):
        return "AI could not generate a review as data was not successfully retrieved for this section."

    prompt_template = f"Provide a concise, neutral summary and review of the following financial data related to {page_name}. Highlight key trends, significant values, or notable observations. Keep it under 200 words.\n\nData: "

    data_str = ""
    for key, value in page_data.items():
        if key not in ["status", "chart_status", "num_data_points", "num_filings", "company", "ticker", "cik", "manager_name", "manager_cik", "date_range", "data_summary"]: # Exclude meta-keys
            data_str += f"{key.replace('_', ' ').title()}: {value}\n"
    
    # For Market Trend Visualization, specifically extract data_summary
    if page_name == "Market Trend Visualization" and "data_summary" in page_data:
        for ds_key, ds_value in page_data["data_summary"].items():
            data_str += f"{ds_key.replace('_', ' ').title()}: {ds_value}\n"


    full_prompt = prompt_template + data_str

    try:
        # --- REPLACE THIS SECTION WITH YOUR ACTUAL LLM CALL ---
        # Uncomment and configure if using Google Gemini:
        # model = genai.GenerativeModel('gemini-1.5-flash') # Or 'gemini-pro', etc.
        # response = model.generate_content(contents=[{"role": "user", "parts": [full_prompt]}])
        # ai_text = response.text
        # --- END OF LLM CALL PLACEHOLDER ---

        # Simulated AI response for demonstration for different pages:
        if page_name == "Nifty 50 Chart":
            start_close = page_data.get("first_close", "N/A")
            end_close = page_data.get("last_close", "N/A")
            min_close = page_data.get("min_close", "N/A")
            max_close = page_data.get("max_close", "N/A")
            if isinstance(start_close, (int, float)): start_close = f"{start_close:.2f}"
            if isinstance(end_close, (int, float)): end_close = f"{end_close:.2f}"
            if isinstance(min_close, (int, float)): min_close = f"{min_close:.2f}"
            if isinstance(max_close, (int, float)): max_close = f"{max_close:.2f}"
            ai_text = (f"The Nifty 50 chart from {page_data.get('start_date')} to {page_data.get('end_date')} shows prices ranging from a low of **{min_close}** to a high of **{max_close}**. "
                       f"The period started at approximately **{start_close}** and ended around **{end_close}**. "
                       f"This reflects the overall movement of the index over **{page_data.get('num_data_points')}** data points, indicating its historical volatility and trend.")
        
        elif page_name == "Financial News":
            ai_text = (f"The search for **{page_data.get('company')}** found **{page_data.get('num_filings')}** recent SEC EDGAR filings. "
                       f"These filings, primarily **Form 8-K**, disclose material events that could impact the company's operations or stock price. "
                       f"Users should review the specific filings for detailed information on these events and their potential implications.")
        
        elif page_name == "Financial Statements":
            company_name = page_data.get('company', 'the company')
            revenue = page_data.get('revenue_last_period', 'N/A')
            net_income = page_data.get('net_income_last_period', 'N/A')
            assets = page_data.get('total_assets_last_period', 'N/A')
            if isinstance(revenue, (int, float)): revenue = f"${revenue:,.0f}"
            if isinstance(net_income, (int, float)): net_income = f"${net_income:,.0f}"
            if isinstance(assets, (int, float)): assets = f"${assets:,.0f}"
            ai_text = (f"The latest financial statements for **{company_name}** indicate recent **revenues of {revenue}**, "
                       f"with a **net income of {net_income}**. "
                       f"Total assets stood at **{assets}**. "
                       f"These figures provide a snapshot of {company_name}'s recent financial health and operational performance, offering a basis for deeper fundamental analysis.")
        
        elif page_name == "Insider Trading":
            company_name = page_data.get('company', 'the company')
            num_filings = page_data.get('num_filings', 'no')
            ai_text = (f"For **{company_name}**, **{num_filings}** recent insider trading filings (Forms 3, 4, 5) were identified. "
                       f"These disclosures signify changes in ownership by corporate insiders, such as executives and directors. "
                       f"While the raw transactions require delving into each filing, the presence of these reports indicates active insider participation, which can sometimes provide signals about management's outlook.")
        
        elif page_name == "Institutional Holdings":
            manager_name = page_data.get('manager_name', 'the institutional manager')
            num_filings = page_data.get('num_filings', 'no')
            ai_text = (f"Recent Form 13F filings for **{manager_name}** indicate **{num_filings}** reports. "
                       f"These quarterly disclosures offer valuable insights into the equity holdings of this major institutional investor, reflecting their investment strategies and market views. "
                       f"Reviewing the detailed filings is essential to understand the specific stocks and positions held by {manager_name}.")
        
        elif page_name == "Direct AI Question": # Specific logic for this page (e.g., Ask_The_AI.py)
            question = page_data.get("question", "a question")
            ai_response = page_data.get("ai_response", "no response")
            ai_text = (f"The AI was asked: '{question}'. The AI provided the following response: '{ai_response}'. "
                       f"This interaction demonstrates the AI's ability to directly answer user queries within the financial domain, or general topics if specified.")
        
        elif page_name == "Market Trend Visualization": # For the Market Trends page (e.g., if you have another page for raw data)
            ticker = page_data.get("ticker", "the selected ticker")
            num_points = page_data.get("data_summary", {}).get("num_data_points", "no")
            min_close = page_data.get('data_summary', {}).get('min_close', 'N/A')
            max_close = page_data.get('data_summary', {}).get('max_close', 'N/A')
            first_close = page_data.get('data_summary', {}).get('first_close', 'N/A')
            last_close = page_data.get('data_summary', {}).get('last_close', 'N/A')

            if isinstance(min_close, (int, float)): min_close = f"{min_close:.2f}"
            if isinstance(max_close, (int, float)): max_close = f"{max_close:.2f}"
            if isinstance(first_close, (int, float)): first_close = f"{first_close:.2f}"
            if isinstance(last_close, (int, float)): last_close = f"{last_close:.2f}"

            ai_text = (f"The market data for **{ticker}** covers **{num_points}** data points from {page_data.get('date_range')}. "
                       f"The close price ranged from **{min_close}** to **{max_close}**, "
                       f"starting at **{first_close}** and ending at **{last_close}**. "
                       f"This provides a foundational view of its historical performance.")
                       
        elif page_name == "Investment Plan":
            ai_text = "The investment plan generated considers user inputs and market conditions to suggest a portfolio strategy. Review the asset allocation and projected returns carefully against your risk tolerance and financial goals."

        elif page_name == "Mutual Fund Research":
            ai_text = "The mutual fund research results provide details on various funds, including their performance, expense ratios, and asset holdings. Evaluate these metrics against your investment objectives."

        elif page_name == "Document Analysis":
            ai_text = "The document analysis provides summarized insights from the uploaded text. Focus on the extracted key information and sentiment to quickly grasp the document's core content."

        elif page_name == "Economic Data":
            ai_text = "The economic data displayed covers various indicators vital for market analysis. Trends in these figures can provide insight into macroeconomic conditions affecting investment decisions."
        
        elif page_name == "Currency Exchange Rate":
            ai_text = "The currency exchange rate data shows historical trends and current values. These rates are crucial for understanding international trade, investment, and the relative strength of economies."

        else:
            ai_text = f"AI review for {page_name} is under development. No specific summary template yet."

        return ai_text

    except Exception as e:
        # st.error(f"Error calling LLM for review: {e}") # You might uncomment this for debugging
        return "AI review generation failed due to an internal error or missing API configuration."

# --- Nifty 50 Page Content ---
st.title("📈 Nifty 50 Historical Chart")

# --- Nifty 50 Ticker ---
NIFTY_TICKER = "^NSEI" # Nifty 50 index ticker on Yahoo Finance

# --- Date Inputs ---
col1, col2 = st.columns(2)
with col1:
    chart_start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=365*2), max_value=datetime.now().date() - timedelta(days=1), key="nifty_start_date")
with col2:
    chart_end_date = st.date_input("End Date", datetime.now().date(), max_value=datetime.now().date(), key="nifty_end_date")

if chart_start_date >= chart_end_date:
    st.error("Error: Start date must be before end date.")
    # Initialize session state for AI summary with error status
    if 'ai_summary_data' not in st.session_state:
        st.session_state['ai_summary_data'] = {}
    st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
        "ticker": NIFTY_TICKER,
        "start_date": chart_start_date.strftime("%Y-%m-%d"),
        "end_date": chart_end_date.strftime("%Y-%m-%d"),
        "status": "Error: Invalid date range."
    }
else:
    if st.button("Generate Chart", key="nifty_generate_chart_btn"):
        with st.spinner("Fetching Nifty 50 data..."):
            try:
                data = yf.download(NIFTY_TICKER, start=chart_start_date, end=chart_end_date)
                
                if data.empty:
                    st.warning("No data found for the selected date range.")
                    if 'ai_summary_data' not in st.session_state:
                        st.session_state['ai_summary_data'] = {}
                    st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                        "ticker": NIFTY_TICKER,
                        "start_date": chart_start_date.strftime("%Y-%m-%d"),
                        "end_date": chart_end_date.strftime("%Y-%m-%d"),
                        "num_data_points": 0,
                        "status": "No data found."
                    }
                else:
                    # --- Data Preprocessing: Handle MultiIndex and ensure numeric types ---
                    # Use the NIFTY_TICKER variable for renaming logic
                    current_page_ticker = NIFTY_TICKER

                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = ['_'.join(col).strip() for col in data.columns.values]
                        
                        column_mapping = {}
                        standard_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                        for std_col in standard_cols:
                            expected_flattened_name = f'{std_col}_{current_page_ticker}'.replace('^', '') # Remove ^ if present
                            if expected_flattened_name in data.columns:
                                column_mapping[expected_flattened_name] = std_col
                            elif std_col in data.columns: # Fallback for already standard names
                                 column_mapping[std_col] = std_col
                        
                        if column_mapping:
                            data = data.rename(columns=column_mapping)
                        else:
                            st.warning("Could not find expected columns to rename after flattening. Chart might not display correctly.")
                    else:
                        # Ensure standard capitalization if not multi-index (e.g., for stocks)
                        data.columns = [col.replace(' ', '_').capitalize() for col in data.columns]

                    # --- Ensure critical columns are numeric and handle missing values ---
                    for col_name in ['Open', 'High', 'Low', 'Close', 'Volume']:
                        if col_name in data.columns:
                            data[col_name] = pd.to_numeric(data[col_name], errors='coerce')
                        else:
                            # Instead of st.stop(), raise an error or set a status
                            raise ValueError(f"Required column '{col_name}' not found after data processing. Cannot plot.")

                    # --- Drop rows with NaN values in crucial plotting columns ---
                    data.dropna(subset=['Open', 'High', 'Low', 'Close'], inplace=True)
                    
                    if data.empty:
                        st.warning("No valid numeric data found for plotting after cleaning.")
                        if 'ai_summary_data' not in st.session_state:
                            st.session_state['ai_summary_data'] = {}
                        st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                            "ticker": NIFTY_TICKER,
                            "start_date": chart_start_date.strftime("%Y-%m-%d"),
                            "end_date": chart_end_date.strftime("%Y-%m-%d"),
                            "num_data_points": 0,
                            "status": "No valid numeric data after cleaning."
                        }
                    else:
                        st.subheader(f"Nifty 50 Price Chart ({chart_start_date} to {chart_end_date})")
                        
                        fig = go.Figure(data=[go.Candlestick(
                            x=data.index,
                            open=data['Open'],
                            high=data['High'],
                            low=data['Low'],
                            close=data['Close']
                        )])

                        fig.update_layout(
                            xaxis_rangeslider_visible=False,
                            height=600,
                            title_text=f"Nifty 50 Candlestick Chart",
                            xaxis_title="Date",
                            yaxis_title="Price",
                            template="plotly_dark"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # --- Update session state with data for AI summary ---
                        if 'ai_summary_data' not in st.session_state:
                            st.session_state['ai_summary_data'] = {}
                        
                        st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                            "ticker": NIFTY_TICKER,
                            "start_date": chart_start_date.strftime("%Y-%m-%d"),
                            "end_date": chart_end_date.strftime("%Y-%m-%d"),
                            "num_data_points": len(data),
                            "first_close": data['Close'].iloc[0],
                            "last_close": data['Close'].iloc[-1],
                            "min_close": data['Close'].min(),
                            "max_close": data['Close'].max(),
                            "status": "Chart generated successfully."
                        }

            except Exception as e:
                st.error(f"An error occurred while fetching or plotting Nifty 50 data: {e}. Please try again.")
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                    "ticker": NIFTY_TICKER,
                    "start_date": chart_start_date.strftime("%Y-%m-%d"),
                    "end_date": chart_end_date.strftime("%Y-%m-%d"),
                    "status": f"Error fetching data: {e}"
                }
    else: # If button not pressed, initialize session state if not already done
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        if 'Nifty 50 Chart' not in st.session_state['ai_summary_data']:
             st.session_state['ai_summary_data']['Nifty 50 Chart'] = {
                "status": "Chart not yet generated."
            }

st.markdown("---")

# --- AI Review Section for Nifty 50 Chart ---
st.subheader("🤖 AI-Powered Review")

page_key_in_session_state = "Nifty 50 Chart"
display_name = "Nifty 50 Chart"

current_page_data = st.session_state.get('ai_summary_data', {}).get(page_key_in_session_state, {})

if current_page_data and current_page_data.get("status") == "Chart generated successfully.":
    if st.button(f"Generate AI Review for {display_name}"):
        with st.spinner("Generating AI review..."):
            review = get_ai_review(display_name, current_page_data)
            st.write(review)
    else:
        st.info(f"Click the button above to get an AI-powered summary of the {display_name} data.")
else:
    st.info(f"No {display_name} data available to generate an AI review. Please generate the chart first.")

st.markdown("---")
