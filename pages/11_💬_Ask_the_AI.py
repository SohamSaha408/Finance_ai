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
        st.warning("The AI could not understand the audio.
