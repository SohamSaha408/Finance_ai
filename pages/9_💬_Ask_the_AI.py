import streamlit as st
import google.generativeai as genai
from utils.styling import set_common_font # Adjust path if your utils folder is structured differently
import streamlit as st
import base64

# --- Function to get base64 encoded image ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- Path to your background image ---
# IMPORTANT: Make sure 'black-particles-background.avif' is in the correct directory
# relative to where your Streamlit app is run from.
# For example, if it's in a subfolder named 'images', the path would be "images/black-particles-background.avif".
background_image_path = "black-particles-background.avif" # Updated path

# --- Get the base64 encoded string and inject CSS ---
try:
    encoded_image = get_base64_image(background_image_path)
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{encoded_image}"); /* Changed mime type to avif */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"Error: Background image not found at '{background_image_path}'. Please check the path for this page.")
except Exception as e:
    st.error(f"An error occurred while setting the background image for this page: {e}")

# --- Your page-specific content starts here ---
# (e.g., st.title, st.write, input widgets, charts, etc.)

st.title("💬 Ask the AI Anything")
st.markdown("<p style='font-size: 1.1rem;'>Have a direct question for the AI about finance, investing, or anything else?</p>", unsafe_allow_html=True)

user_question_direct = st.text_area("Your Question:", key="atai_direct_ai_question_area") # Unique key

if st.button("Ask AI", key="atai_ask_ai_btn"): # Unique key
    if user_question_direct:
        try:
            genai.configure(api_key=st.secrets["gemini"]["api_key"])
        except KeyError:
            st.error("Gemini API key not found in Streamlit secrets. Please ensure .streamlit/secrets.toml is correctly configured with `gemini.api_key`.")
            st.stop()

        model = genai.GenerativeModel('gemini-1.5-flash')

        with st.spinner("Getting AI's response..."):
            try:
                prompt = (
                    "You are a helpful and expert Indian financial advisor. Provide a concise and accurate answer to the following question. "
                    "If the question is not financial, answer generally but remind the user this is a financial advisor tool. "
                    "Keep answers focused and professional.\n\n"
                    f"User: {user_question_direct}\n\n"
                    "AI Advisor:"
                )
                response = model.generate_content(contents=[{"role": "user", "parts": [prompt]}])
                st.subheader("🤖 AI's Answer:")
                st.markdown(f"<p style='color: white;'>{response.text}</p>", unsafe_allow_html=True)

                # --- Capture for AI Summary ---
                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Direct AI Question'] = {
                    "question": user_question_direct,
                    "ai_response": response.text
                }
            except Exception as e:
                st.error(f"Error communicating with Gemini AI: {e}. Please try again.")
    else:
        st.warning("Please enter your question for the AI.")

st.markdown("---")
