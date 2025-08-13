import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎥 YouTube Video Summarizer (Hebrew & English)")

youtube_url = st.text_input("Paste a YouTube link:")

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    # Try Hebrew first
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['he'])
        return " ".join([t['text'] for t in transcript_data]), "he"
    except:
        pass

    # Then try English
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return " ".join([t['text'] for t in transcript_data]), "en"
    except:
        pass

    raise Exception("No subtitles found in Hebrew or English.")

def summarize_text(text, language):
    if language == "he":
        prompt = f"סכם את הטקסט הבא בצורה פשוטה וברורה בעברית:\n\n{text}"
    else:
        prompt = f"Summarize the following text in simple and clear English:\n\n{text}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message["content"]

if youtube_url:
    try:
        video_id = extract_video_id(youtube_url)
        with st.spinner("📄 Fetching transcript..."):
            transcript_text, lang = get_transcript(video_id)

        with st.spinner("📝 Summarizing..."):
            summary = summarize_text(transcript_text, lang)

        st.subheader("Summary:")
        st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")
