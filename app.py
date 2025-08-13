import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎥 YouTube Video Summarizer (Hebrew Preferred)")

youtube_url = st.text_input("Paste a YouTube link:")

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        # Try Hebrew first
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'iw'])
        return " ".join([t['text'] for t in transcript]), "he"
    except:
        try:
            # Try English if Hebrew fails
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            return " ".join([t['text'] for t in transcript]), "en"
        except Exception as e:
            raise Exception("No subtitles found in Hebrew or English.")

def summarize_text(text):
    prompt = f"סכם את הטקסט הבא בצורה פשוטה וברורה בעברית:\n\n{text}"
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
            summary = summarize_text(transcript_text)

        st.subheader("סיכום:")
        st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")
