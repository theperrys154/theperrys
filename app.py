import streamlit as st
import yt_dlp
import os
from pathlib import Path

# Load API key from Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

st.title("YouTube Audio Downloader")

# --- Function to download audio from YouTube ---
def download_audio_from_youtube(url):
    output_file = "audio.mp3"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_file,
        "quiet": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_file

# --- Streamlit UI ---
youtube_url = st.text_input("Enter YouTube video URL")

if st.button("Download Audio"):
    if youtube_url.strip():
        try:
            audio_path = download_audio_from_youtube(youtube_url)
            st.success("Download complete!")
            st.audio(audio_path)
        except Exception as e:
            st.error(f"Error downloading audio: {e}")
    else:
        st.warning("Please enter a valid YouTube URL")
