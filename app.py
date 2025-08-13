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

def get_best_transcript(video_id):
    try:
        # This returns a list of available transcripts with language codes
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try Hebrew first
        for transcript in transcripts:
            if 'he' in transcript.language_code or 'iw' in transcript.language_code:
                return " ".join([t['text'] for t in transcript.fetch()]), "he"

        # Try English
        for transcript in transcripts:
            if transcript.language_code.startswith('en'):
                return " ".join([t['text'] for t in transcript.fetch()]), "en"

        # If nothing matches, just take the first one
        first = transcripts.find_transcript([t.language_code for t in transcripts])
        return " ".join([t['text'] for t in first.fetch()]), first.language_code

    except Exception as e:
        raise Exception(f"Transcript error: {e}")

def summarize_text(text, language):
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
            transcript_text, lang = get_best_transcript(video_id)

        with st.spinner("📝 Summarizing..."):
            summary = summarize_text(transcript_text, lang)

        st.subheader("סיכום:")
        st.write(summary)

    except Exception as e:
        st.error(f"Error: {e}")
