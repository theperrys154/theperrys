from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st
import openai

st.title("סיכום סרטוני YouTube בעברית")

video_url = st.text_input("הדבק כאן קישור ל-YouTube")

if video_url:
    try:
        video_id = video_url.split("v=")[-1]
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['he'])
        
        text = " ".join([t['text'] for t in transcript])
        
        st.subheader("סיכום בעברית")
        # כאן נשתמש ב-OpenAI לסיכום
        openai.api_key = st.secrets["OPENAI_API_KEY"]
        summary = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "אתה מסכם טקסט בעברית בצורה ברורה וקצרה."},
                {"role": "user", "content": text}
            ]
        )
        st.write(summary.choices[0].message["content"])
    except Exception as e:
        st.error(f"שגיאה: {str(e)}")
