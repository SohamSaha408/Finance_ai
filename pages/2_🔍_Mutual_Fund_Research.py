import streamlit as st
from advisor import search_funds # Ensure advisor.py is in the main directory

st.title("🔍 Mutual Fund Research")
st.markdown("<p style='font-size: 1.1rem;'>Search for mutual funds by name to get details.</p>", unsafe_allow_html=True)

search_query = st.text_input("Enter fund name to search", key="mfr_fund_search_input") # Unique key

if search_query:
    funds = search_funds(search_query)
    found_funds_info = []
    if funds:
        st.subheader("Top 5 Search Results:")
        for fund in funds[:5]:
            st.markdown(f"<p style='color: white;'><b>{fund['schemeName']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: white;'>Scheme Code: {fund.get('schemeCode', 'N/A')}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: white;'>[Live NAV](https://api.mfapi.in/mf/{fund.get('schemeCode', '')})</p>", unsafe_allow_html=True)
            st.markdown("---")
            found_funds_info.append(f"{fund['schemeName']} (Code: {fund.get('schemeCode', 'N/A')})")
        # --- Capture for AI Summary ---
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        st.session_state['ai_summary_data']['Mutual Fund Research'] = {
            "query": search_query,
            "results": f"Found {len(funds)} funds. Top 5: {', '.join(found_funds_info)}"
        }
    else:
        st.markdown("<p style='color: white;'>No funds found for your query.</p>", unsafe_allow_html=True)
        if 'ai_summary_data' not in st.session_state:
            st.session_state['ai_summary_data'] = {}
        st.session_state['ai_summary_data']['Mutual Fund Research'] = {
            "query": search_query,
            "results": "No funds found."
        }
st.markdown("---")
