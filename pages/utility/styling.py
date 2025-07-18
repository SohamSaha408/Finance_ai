# utils/styling.py
import streamlit as st

def set_common_font():
    st.markdown(
        """
        <style>
        html, body, .stApp {
            font-family: 'Arial', sans-serif; /* Replace 'Arial' with your desired font */
        }
        /* You can add more specific selectors if needed */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Verdana', sans-serif; /* Example: different font for headings */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
