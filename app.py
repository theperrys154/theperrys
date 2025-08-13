import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import openai

# Load API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("🎥 YouTube Video Summarizer")
st.write("Paste a YouTube link below and get an easy-to-read summary.")

# Step 1: Get YouTube URL
youtube_url = st.text_input("Enter YouTube Video URL:")

def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        return parse_qs(parsed_url.query).get('v', [None])[0]
    return None

if youtube_url:
    video_id = get_video_id(youtube_url)
    if video_id:
        try:
            # Step 2: Get transcript
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            transcript_text = " ".join([t['text'] for t in transcript_list])

            # Step 3: Summarize with GPT
            with st.spinner("Summarizing video..."):
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes YouTube videos into clear, simple explanations."},
                        {"role": "user", "content": f"Summarize this transcript into an easy and comfortable text:\n\n{transcript_text}"}
                    ],
                    max_tokens=500
                )
                summary = response.choices[0].message.content

            st.subheader("📝 Summary")
            st.write(summary)

        except Exception as e:
            st.error(f"Error: {e}\nThe video might not have subtitles.")
    else:
        st.error("Invalid YouTube URL. Please check and try again.")
