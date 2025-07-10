import streamlit as st
import base64
import os

# IMPORTANT: st.set_page_config MUST be the first Streamlit command
st.set_page_config(page_title="AI Financial Advisor", layout="centered")

# --- Background and Initial CSS ---
# Ensure your 'black-particles-background.avif' file is in the same directory as Home.py
def set_background(image_file):
    if not os.path.exists(image_file):
        st.error(f"Background image not found: '{image_file}'. Please ensure the image is in the correct directory.")
        fallback_css = """<style>.stApp {background-color: #222222; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;}</style>"""
        st.markdown(fallback_css, unsafe_allow_html=True)
        return

    try:
        with open(image_file, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        css = f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        .main .block-container {{
            background-color: rgba(0, 0, 0, 0.75); padding: 2rem; border-radius: 1rem; margin: 2rem auto;
            max-width: 700px; width: 90%; color: white; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(5px); -webkit-backdrop-filter: blur(5px); overflow: auto;
        }}
        .stMarkdown, .stText, .stLabel, .stTextInput > div > label, .stNumberInput > label, .stSelectbox > label, .stTextArea > label {{
            color: white !important;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #E0E0E0 !important; text-shadow: 1px 1px 3px rgba(0,0,0,0.7);
        }}
        .stButton>button {{
            background-color: #34495e; /* Dark blue-gray for harmony */
            color: white; border-radius: 0.5rem; border: none;
            padding: 0.75rem 1.5rem; font-size: 1rem; cursor: pointer; transition: background-color 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #44607a; /* Slightly lighter blue-gray on hover */
        }}
        .stTextInput, .stNumberInput, .stSelectbox, .stTextArea {{
            background-color: rgba(0, 0, 0, 0.4); /* Darker semi-transparent for inputs */
            border-radius: 0.5rem; padding: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        .stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea {{
            color: white; background-color: transparent; border: none;
        }}
        .stSelectbox > div > div[data-baseweb="select"] > div[role="button"] {{
            color: white; background-color: transparent; border: none;
        }}
        .stSelectbox div[data-baseweb="select"] div[role="listbox"] {{
            background-color: rgba(0, 0, 0, 0.9); color: white;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Background image not found: '{image_file}'. Please ensure the image is in the correct directory.")
        fallback_css = """<style>.stApp {background-color: #222222; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;}</style>"""
        st.markdown(fallback_css, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An unexpected error occurred while setting background: {e}")
        fallback_css = """<style>.stApp {background-color: #222222; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;}</style>"""
        st.markdown(fallback_css, unsafe_allow_html=True)

set_background("black-particles-background.avif")

st.title("💸 Welcome to Your AI Financial Advisor")

st.markdown("""
<p style='font-size: 1.2rem;'>
    Your intelligent partner for all things finance! Explore various tools designed to help you with investment planning, market research, document analysis, and much more.
</p>
""", unsafe_allow_html=True)

st.header("How to Use This App:")
st.markdown("""
<p style='font-size: 1.1rem;'>
    Use the **navigation links in the sidebar** to explore different features of the application.
    Each page focuses on a specific aspect of financial advisory.
</p>
""", unsafe_allow_html=True)

st.subheader("Features include:")
st.markdown("""
<ul>
    <li>📊 Investment Planning: Get personalized advice based on your profile and goals.</li>
    <li>🔍 Mutual Fund Research: Search for and get details on mutual funds.</li>
    <li>📄 Document Analyzer: Upload and analyze financial documents with AI.</li>
    <li>📈 Economic Data (FRED): Explore key economic indicators.</li>
    <li>📊 Market Trends Data: Access historical data for stocks and indices.</li>
    <li>📰 Latest Financial News: Stay updated with real-time financial news.</li>
    <li>🏢 Company Financials: Dive into detailed company financial statements.</li>
    <li>🧠 AI Summary: Get a consolidated AI overview of your activities.</li>
    <li>💬 Ask the AI: Pose direct financial questions to the AI.</li>
</ul>
""", unsafe_allow_html=True)

st.markdown("---")
st.info("Developed with Streamlit and advanced AI models for a smarter financial experience.")

# Initialize session state for AI summary inputs. This should be done once.
if 'ai_summary_data' not in st.session_state:
    st.session_state['ai_summary_data'] = {}

# The JavaScript for scrolling is no longer needed in multi-page apps.
