import streamlit as st
import google.generativeai as genai
import speech_recognition as sr
from st_audiorecorder import st_audiorecorder
import io

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
# 2. VOICE-TO-TEXT FUNCTIONALITY
# ====================================================================

def recognize_speech():
    """
    Displays the audio recorder and processes the recorded audio
    to return the recognized text.
    """
    st.write("#### Ask with your voice 🎙️")
    audio_bytes = st_audiorecorder(pause_threshold=2.0)
    
    if not audio_bytes:
        return None # No audio recorded

    st.info("Audio recorded. Processing...")
    try:
        # Create an in-memory WAV file
        wav_file = io.BytesIO(audio_bytes)
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(wav_file) as source:
            audio_data = recognizer.record(source)
        
        # Recognize speech using Google's free API
        recognized_text = recognizer.recognize_google(audio_data)
        st.success("Speech recognized!")
        return recognized_text

    except sr.UnknownValueError:
        st.warning("The AI could not understand the audio. Please try again.")
        return None
    except sr.RequestError as e:
        st.error(f"Could not request results from speech recognition service; {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred during speech recognition: {e}")
        return None

# ====================================================================
# 3. MAIN PAGE UI & LOGIC
# ====================================================================

st.title("💬 Ask the AI Anything")
st.markdown("Use your voice or the text box below to ask the AI a question.")

# Initialize the session state for the question if it doesn't exist
if 'ask_ai_question' not in st.session_state:
    st.session_state.ask_ai_question = ""

# --- Voice Input ---
recognized_text = recognize_speech()
if recognized_text:
    # If speech was recognized, update the text area and rerun
    st.session_state.ask_ai_question = recognized_text
    st.rerun()

# --- Text Input ---
user_question = st.text_area(
    "Your Question:", 
    value=st.session_state.ask_ai_question,
    height=150
)

# --- Submit Button & AI Response ---
if st.button("Ask AI"):
    if user_question:
        try:
            # Configure the Gemini API key
            api_key = st.secrets["gemini"]["api_key"]
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')

            # Show a spinner while waiting for the AI
            with st.spinner("🤖 The AI is thinking..."):
                prompt = (
                    "You are a helpful financial advisor. Answer the following user question "
                    "concisely and professionally.\n\n"
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
