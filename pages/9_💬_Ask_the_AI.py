import streamlit as st
import google.generativeai as genai

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
