import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader # Make sure pypdf is installed (pip install pypdf)
import os # For os.path.splitext
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
st.title("📄 Document Analyzer")

st.set_page_config(page_title="Document Analyzer", page_icon="📄", layout="wide")

st.write("Upload and analyze financial documents (e.g., earnings reports, prospectuses) to quickly extract key information, summarize content, and identify important insights. Leverage AI for efficient document review.")
# ... rest of your page code ...
st.markdown("<p style='font-size: 1.1rem;'>Upload a document (PDF or TXT) for the AI to analyze and provide insights.</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"], key="da_doc_uploader") # Unique key

def get_pdf_text(pdf_file):
    text = ""
    try:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
    return text

document_text = ""
if uploaded_file is not None:
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()

    if file_extension == ".pdf":
        st.info("Extracting text from PDF... This may take a moment for large files.")
        document_text = get_pdf_text(uploaded_file)
    elif file_extension == ".txt":
        st.info("Reading text from TXT file...")
        document_text = uploaded_file.getvalue().decode("utf-8")
    else:
        st.warning("Unsupported file type. Please upload a PDF or TXT file.")

    if document_text:
        st.subheader("Extracted Document Text (Preview)")
        preview_text = document_text[:1000]
        if len(document_text) > 1000:
            preview_text += "\n\n... (Document truncated for preview. Full content sent to AI.)"
        st.text_area("Document Content", preview_text, height=300, disabled=True, key="da_doc_preview") # Unique key

        st.markdown("---")
        st.subheader("Ask AI about this Document")
        document_question = st.text_area("What do you want to know or analyze about this document?", key="da_doc_ai_question_area") # Unique key

        if st.button("Analyze Document", key="da_analyze_doc_btn"): # Unique key
            if document_question:
                try:
                    genai.configure(api_key=st.secrets["gemini"]["api_key"])
                except KeyError:
                    st.error("Gemini API key not found in Streamlit secrets. Please ensure .streamlit/secrets.toml is correctly configured with `gemini.api_key`.")
                    st.stop()

                model = genai.GenerativeModel('gemini-1.5-flash')

                with st.spinner("Analyzing document..."):
                    try:
                        prompt = (
                            f"You are a helpful and expert Indian financial advisor. Analyze the following document and provide advice/answers based on the user's question.\n\n"
                            f"--- Document Content ---\n{document_text}\n\n"
                            f"--- User Question ---\n{document_question}\n\n"
                            f"--- Financial Advice/Analysis ---"
                        )
                        response = model.generate_content(contents=[{"role": "user", "parts": [prompt]}])
                        st.subheader("🤖 AI's Document Analysis:")
                        st.markdown(f"<p style='color: white;'>{response.text}</p>", unsafe_allow_html=True)
                        # --- Capture for AI Summary ---
                        if 'ai_summary_data' not in st.session_state:
                            st.session_state['ai_summary_data'] = {}
                        st.session_state['ai_summary_data']['Document Analysis'] = {
                            "document_question": document_question,
                            "ai_response": response.text
                        }
                    except Exception as e:
                        st.error(f"Error calling Gemini AI for document analysis: {e}. This might be due to model token limits or other API issues. Try a shorter document or question.")
            else:
                st.warning("Please enter a question to analyze the document.")
    else:
        st.warning("Could not extract text from the uploaded document. Please try another file or ensure it's a readable PDF/TXT.")
st.markdown("---")
