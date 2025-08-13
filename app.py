import streamlit as st
import openai
import tempfile
import os
import json
from pytube import YouTube
import whisper

# ==============================
# CONFIGURATION
# ==============================
# Get secrets from Streamlit Cloud settings (safe way)
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
MODEL_SUMMARY = st.secrets.get("MODEL_SUMMARY", "gpt-4o-mini")
WHISPER_MODEL = st.secrets.get("WHISPER_MODEL", "base")

# Set the API key
openai.api_key = OPENAI_API_KEY

# ==============================
# FUNCTIONS
# ==============================
def download_audio_from_youtube(url):
    """Download audio from YouTube and return file path."""
    yt = YouTube(url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    audio_stream.download(filename=temp_file.name)
    return temp_file.name

def transcribe_audio(file_path):
    """Transcribe audio using Whisper."""
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(file_path)
    return result["text"]

def summarize_text(text):
    """Summarize text using OpenAI."""
    prompt = f"Summarize the following text in a clear and concise way:\n\n{text}"
    response = openai.ChatCompletion.create(
        model=MODEL_SUMMARY,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message["content"]

# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="YouTube Video Summarizer", page_icon="🎥")
st.title("🎥 YouTube Video Summarizer")

# Input for YouTube URL
youtube_url = st.text_input("Enter YouTube video URL:")

if youtube_url:
    with st.spinner("Downloading audio..."):
        audio_path = download_audio_from_youtube(youtube_url)

    with st.spinner("Transcribing audio..."):
        transcription = transcribe_audio(audio_path)

    with st.spinner("Summarizing transcription..."):
        summary = summarize_text(transcription)

    st.subheader("📄 Summary")
    st.write(summary)

    st.subheader("📝 Full Transcription")
    with st.expander("Show Transcription"):
        st.write(transcription)

    # Cleanup temporary file
    os.remove(audio_path)
