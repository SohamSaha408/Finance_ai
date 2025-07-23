import streamlit as st
import base64
import os
import json
import bcrypt

# =================================================================
# 1. AUTHENTICATION AND REGISTRATION LOGIC
# This function handles the entire login/signup process.
# =================================================================
def authentication_gate():
    """Handles both login and registration."""
    if st.session_state.get("logged_in", False):
        return True

    st.set_page_config(page_title="Welcome", layout="centered")
    st.title("Welcome to Your Financial AI Dashboard")

    choice = st.radio("Choose an action:", ("Login", "Sign Up"), horizontal=True)

    # --- LOGIN LOGIC ---
    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            try:
                with open("users.json", 'r') as f: users = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError): users = {}

            if username in users and bcrypt.checkpw(password.encode(), users[username].encode()):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error("Incorrect username or password")

    # --- SIGN UP LOGIC ---
    elif choice == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("New Username", key="signup_username")
        new_password = st.text_input("New Password", type="password", key="signup_password")

        if st.button("Sign Up"):
            if not new_username or not new_password:
                st.warning("Please enter both a username and a password.")
            else:
                try:
                    with open("users.json", 'r') as f: users = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError): users = {}

                if new_username in users:
                    st.error("This username is already taken. Please choose another.")
                else:
                    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                    users[new_username] = hashed_pw
                    with open("users.json", 'w') as f:
                        json.dump(users, f, indent=4)
                    st.success("Account created successfully! Please switch to the Login tab to log in.")
    
    return False

# =================================================================
# 2. HELPER FUNCTION FOR BACKGROUND AND STYLING
# This function sets the background image and custom CSS.
# =================================================================
def set_background(image_file):
    if not os.path.exists(image_file):
        st.error(f"Background image not found: '{image_file}'. Using fallback color.")
        st.markdown("""<style>.stApp {background-color: #222222;}</style>""", unsafe_allow_html=True)
        return
    
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    
    # This is the more detailed CSS from your code
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{encoded}");
        background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    /* Other styles can be added here if needed */
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# =================================================================
# 3. MAIN APPLICATION LOGIC
# This is the gate. The code inside this 'if' block will only
# run if the user is successfully logged in.
# =================================================================
if authentication_gate():

    # IMPORTANT: st.set_page_config() must be the first Streamlit command for the main app.
    st.set_page_config(
        page_title="AI Financial Advisor",
        page_icon="💸",
        layout="wide" 
    )

    # --- Call the function to set the background ---
    set_background("black-particles-background.avif")

    # --- Sidebar with Logout Button ---
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state['username']}**!")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            st.rerun()
        st.markdown("---")
        # You can add your navigation links here
        st.header("Navigation")
        # Example: st.page_link("pages/dashboard.py", label="Dashboard")
    
    # --- Main Page Content ---
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

    # Initialize session state for other parts of your app if needed
    if 'ai_summary_data' not in st.session_state:
        st.session_state['ai_summary_data'] = {}
