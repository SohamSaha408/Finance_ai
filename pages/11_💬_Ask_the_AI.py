import streamlit as st
import google.generativeai as genai
import base64
from st_audiorecorder import st_audiorecorder
import speech_recognition as sr
import io

# --- Function to get base64 encoded image ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        # We'll just ignore the error if the background is not found
        return None

# --- Path to your background image ---
background_image_path = "black-particles-background.avif"

# --- Get the base64 encoded string and inject CSS ---
encoded_image = get_base64_image(background_image_path)
if encoded_image:
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/avif;base64,{encoded_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)

# --- Initialize session state for the text area ---
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""

# --- Page Content ---
st.title("💬 Ask the AI Anything")
st.markdown("<p style='font-size: 1.1rem;'>Have a direct question for the AI about finance, investing, or anything else?</p>", unsafe_allow_html=True)

# --- VOICE INTEGRATION: RECORD AND CONVERT ---
st.write("#### Ask with your voice 🎙️")
st.write("Click the microphone to start/stop recording.")
audio_bytes = st_audiorecorder(pause_threshold=2.0, key="audio_recorder")

if audio_bytes:
    st.info("Audio detected, processing...")
    try:
        wav_file = io.BytesIO(audio_bytes)
        r = sr.Recognizer()
        with sr.AudioFile(wav_file) as source:
            audio_data = r.record(source)
        
        st.info("Sending audio for recognition...")
        recognized_text = r.recognize_google(audio_data)
        
        st.success(f"Recognized text: \"{recognized_text}\"")
        st.session_state.user_question = recognized_text
        st.rerun()

    except sr.UnknownValueError:
        st.warning("The AI could not understand the audio. Please try speaking more clearly.")
    except sr.RequestError as e:
        st.error(f"Speech recognition service is unavailable. Error: {e}")
    except Exception as e:
        st.error(f"An unexpected error occurred during audio processing: {e}")

# The text area will now use the session state value
user_question_direct = st.text_area(
    "Your Question:", 
    value=st.session_state.user_question, 
    key="atai_direct_ai_question_area"
) 

if st.button("Ask AI", key="atai_ask_ai_btn"):
    if user_question_direct:
        try:
            genai.configure(api_key=st.secrets["gemini"]["api_key"])
        except (KeyError, AttributeError):
            st.error("Gemini API key not found. Please configure your Streamlit secrets.")
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
                st.markdown(f"<div style='color: white; border: 1px solid #444; padding: 10px; border-radius: 5px;'>{response.text}</div>", unsafe_allow_html=True)

                if 'ai_summary_data' not in st.session_state:
                    st.session_state['ai_summary_data'] = {}
                st.session_state['ai_summary_data']['Direct AI Question'] = {
                    "question": user_question_direct,
                    "ai_response": response.text
                }
            except Exception as e:
                st.error(f"Error communicating with Gemini AI: {e}")
    else:
        st.warning("Please enter your question for the AI.")

st.markdown("---")
