import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎥 יוטיוב מסכם בעברית")

youtube_url = st.text_input("הדבק כאן את קישור היוטיוב:")

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    return match.group(1) if match else None

def get_hebrew_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he', 'iw'])
        return " ".join([t['text'] for t in transcript])
    except:
        raise Exception("לא נמצאו כתוביות בעברית.")

def summarize_in_hebrew(text):
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
        with st.spinner("📄 מוריד כתוביות בעברית..."):
            transcript_text = get_hebrew_transcript(video_id)

        with st.spinner("📝 מסכם..."):
            summary = summarize_in_hebrew(transcript_text)

        st.subheader("הסיכום:")
        st.write(summary)

    except Exception as e:
        st.error(f"שגיאה: {e}")
