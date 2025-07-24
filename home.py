import streamlit as st
import base64
import os
import json
import bcrypt
import sqlite3

# =================================================================
# 1. PAGE CONFIGURATION (MUST BE THE FIRST STREAMLIT COMMAND)
# =================================================================
st.set_page_config(
    page_title="Financial Advisor",
    page_icon="💸",
    layout="centered" 
)

# =================================================================
# 2. AUTHENTICATION AND REGISTRATION LOGIC
# =================================================================
def authentication_gate():
    """Handles both login and registration using an SQLite database."""
    if st.session_state.get("logged_in", False):
        return True

    st.title("Welcome to Your Financial AI Dashboard")

    choice = st.radio("Choose an action:", ("Login", "Sign Up"), horizontal=True)

    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False

    # --- LOGIN LOGIC ---
    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()

            if result and bcrypt.checkpw(password.encode(), result[0]):
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                # FIXED THE TYPO HERE
                user_id_result = cursor.fetchone()
                
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["user_id"] = user_id_result[0]
                conn.close()
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
                    hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                    cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (new_username, hashed_pw))
                    conn.commit()
                    st.success("Account created successfully! Please switch to the Login tab to log in.")
                except sqlite3.IntegrityError:
                    st.error("This username is already taken. Please choose another.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

    conn.close()
    return False

# =================================================================
# 3. HELPER FUNCTION FOR BACKGROUND STYLING
# =================================================================
def set_background(image_file):
    if not os.path.exists(image_file):
        # We won't show an error, just use a fallback color
        st.markdown("""<style>.stApp {background-color: #222222;}</style>""", unsafe_allow_html=True)
        return
    
    with open(image_file, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{encoded}");
        background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# =================================================================
# 4. MAIN APPLICATION LOGIC (THE GATE)
# =================================================================
if authentication_gate():
    # --- This part runs only after a successful login ---

    # Set the background for the main app
    set_background("black-particles-background.avif")

    # --- Sidebar with Logout Button ---
    with st.sidebar:
        st.write(f"Welcome, **{st.session_state['username']}**!")
        if st.button("Logout"):
            st.session_state["logged_in"] = False
            # Clear other session state variables if needed
            st.session_state.pop("username", None)
            st.session_state.pop("user_id", None)
            st.rerun()
        st.markdown("---")
        st.header("Navigation")
        # Add your st.page_link() items here for other pages
    
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
    </p>
    """, unsafe_allow_html=True)

    st.subheader("Features include:")
    st.markdown("""
    <ul>
        <li>📊 Investment Planning</li>
        <li>🔍 Mutual Fund Research</li>
        <li>📄 Document Analyzer</li>
        <li>... and more!</li>
    </ul>
    """, unsafe_allow_html=True)
