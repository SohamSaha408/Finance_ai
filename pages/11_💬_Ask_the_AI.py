import streamlit as st
import google.generativeai as genai

# ====================================================================
# 1. PAGE CONFIGURATION & AUTHENTICATION
# ====================================================================

# Set the page configuration
st.set_page_config(
    page_title="Ask the AI",
    page_icon="💬"
)

# Authentication Guard:
# This ensures that only logged-in users can access this page.
if not st.session_state.get("logged_in", False):
    st.error("🔒 Please log in to access this page.")
    st.stop() # Stop the script from running further

# ====================================================================
# 2. MAIN PAGE UI & LOGIC
# ====================================================================

st.title("💬 Ask the AI Anything")
st.markdown("Use the text box below to ask the AI a question about finance or any other topic.")

# --- Text Input ---
user_question = st.text_area(
    "Your Question:",
    height=150,
    placeholder="Type your financial question here..."
)

# --- Submit Button & AI Response ---
if st.button("Ask AI"):
    if user_question:
        try:
            # Configure the Gemini API key from Streamlit secrets
            api_key = st.secrets["gemini"]["api_key"]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Show a spinner while waiting for the AI
            with st.spinner("🤖 The AI is thinking..."):
                prompt = (
                    "You are a helpful and expert Indian financial advisor. Provide a detailed and comprehensive answer to the following question. "
                    "Explain the key concepts, provide relevant context, and use examples where helpful. "
                    "If the question is not financial, answer it thoroughly but gently remind the user that your primary expertise is in finance.\n\n"
                    f"User: {user_question}\n\n"
                    "AI Advisor:"
                )
                response = model.generate_content(prompt)
                
                # Display the response
                st.subheader("🤖 AI's Answer")
                st.markdown(response.text)

        except KeyError:
            st.error("Gemini API key is not configured in your Streamlit secrets.")
        except Exception as e:
            st.error(f"An error occurred while communicating with the AI: {e}")
    else:
        st.warning("Please enter a question first.")
