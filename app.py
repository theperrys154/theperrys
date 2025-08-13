import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎥 מסכם סרטוני יוטיוב בעברית")

youtube_url = st.text_input("הדבק כאן את קישור היוטיוב:")

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    return match.group(1) if match else None

def get_transcript_old(video_id):
    try:
        transcripts, _ = YouTubeTranscriptApi.get_transcripts([video_id], languages=['he'])
        transcript = transcripts[video_id]
        return " ".join([t['text'] for t in transcript])
    except:
        try:
            transcripts, _ = YouTubeTranscriptApi.get_transcripts([video_id], languages=['en'])
            transcript = transcripts[video_id]
            return " ".join([t['text'] for t in transcript])
        except Exception as e:
            raise Exception(f"לא נמצאו כתוביות בעברית או באנגלית: {e}")

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
        with st.spinner("📄 מוריד כתוביות..."):
            transcript_text = get_transcript_old(video_id)

        with st.spinner("📝 מסכם לעברית..."):
            summary = summarize_in_hebrew(transcript_text)

        st.subheader("הסיכום:")
        st.write(summary)

    except Exception as e:
        st.error(f"שגיאה: {e}")
