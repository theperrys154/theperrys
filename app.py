import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re

# Set your API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎥 YouTube Video Summarizer (Hebrew & English)")

# Step 1: Get YouTube link from user
youtube_url = st.text_input("Paste a YouTube link:")

def extract_video_id(url):
    match = re.search(r"(?:v=|youtu\.be/)([^&]+)", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    # Try Hebrew first
    try:
        transcript = transcript_list.find_manually_created_transcript(['he'])
    except:
        try:
            transcript = transcript_list.find_generated_transcript(['he'])
        except:
            transcript = None

    # If no Hebrew, try English
    if transcript is None:
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                transcript = None

    if transcript is None:
        raise Exception("No subtitles available in Hebrew or English.")

    transcript_data = transcript.fetch()
    return " ".join([t['text'] for t in transcript_data]), transcript.language_code

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
        with st.spinner("Fetching transcript..."):
            transcript_text, lang = get_transcript(video_id)

        with st.spinner("Summarizing..."):
            summary = summarize_text(transcript_text, lang)

        st.subheader("📄 Summary:")
        st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")
