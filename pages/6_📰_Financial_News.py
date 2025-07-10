import streamlit as st
import pandas as pd
import requests # Make sure requests is installed (pip install requests)

st.title("📰 Latest Financial News")
st.markdown("<p style='font-size: 1.1rem;'>Current top financial headlines from around the world.</p>", unsafe_allow_html=True)

def get_financial_news(query="finance OR economy OR stock market OR investing", language="en", page_size=5):
    try:
        news_api_key = st.secrets["newsapi"]["api_key"]
        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&"
            f"language={language}&"
            f"sortBy=publishedAt&"
            f"pageSize={page_size}&"
            f"apiKey={news_api_key}"
        )
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])
        return articles
    except KeyError:
        st.error("NewsAPI API key not found in Streamlit secrets. Please set it as `newsapi.api_key`.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching news from NewsAPI.org: {e}")
        return []
    except Exception as e:
        st.error(f"An unexpected error occurred while fetching news: {e}")
        return []

if st.button("Refresh News", key="fn_refresh_news_btn"): # Unique key
    with st.spinner("Fetching latest news..."):
        articles = get_financial_news(query="finance OR economy OR stock market OR investing", language="en", page_size=5)
        news_summary_list = []
        if articles:
            for i, article in enumerate(articles):
                st.subheader(f"{i+1}. {article.get('title', 'No Title')}")
                published_date = article.get('publishedAt')
                if published_date:
                    try:
                        published_date = pd.to_datetime(published_date).strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        published_date = "N/A"
                else:
                    published_date = "N/A"
                st.write(f"**Source:** {article.get('source', {}).get('name', 'N/A')} - **Published:** {published_date}")
                st.write(article.get('description', 'No description available.'))
                st.markdown(f"[Read Full Article]({article.get('url', '#')})")
                st.markdown("---")
                news_summary_list.append(f"Title: {article.get('title', 'N/A')}, Source: {article.get('source', {}).get('name', 'N/A')}, Description: {article.get('description', 'N/A')[:150]}...")
            # --- Capture for AI Summary ---
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Financial News'] = {
                "number_of_articles": len(articles),
                "articles_summary": "\n".join(news_summary_list)
            }
        else:
            st.info("Could not fetch financial news at this moment. Please try again later.")
            if 'ai_summary_data' not in st.session_state:
                st.session_state['ai_summary_data'] = {}
            st.session_state['ai_summary_data']['Financial News'] = {
                "number_of_articles": 0,
                "articles_summary": "No news articles fetched."
            }
st.markdown("---")
