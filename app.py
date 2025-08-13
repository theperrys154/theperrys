import os
import json
import tempfile
from pytube import YouTube
import whisper
from openai import OpenAI

# Load config
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError(f"{CONFIG_FILE} not found. Create it with your API key and preferences.")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

OPENAI_API_KEY = config.get("OPENAI_API_KEY")
MODEL_SUMMARY = config.get("MODEL_SUMMARY", "gpt-4o-mini")
WHISPER_MODEL = config.get("WHISPER_MODEL", "base")

client = OpenAI(api_key=OPENAI_API_KEY)

def download_audio(youtube_url):
    yt = YouTube(youtube_url)
    print(f"Downloading: {yt.title}")
    stream = yt.streams.filter(only_audio=True).first()
    temp_dir = tempfile.gettempdir()
    audio_path = stream.download(output_path=temp_dir, filename="video_audio.mp4")
    return audio_path

def transcribe_audio(audio_path):
    print("Transcribing audio...")
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text):
    print("Summarizing transcript...")
    prompt = f"Summarize this transcript into a clear, concise, and easy-to-read summary:\n\n{text}"
    response = client.chat.completions.create(
        model=MODEL_SUMMARY,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

def summarize_youtube_video(youtube_url):
    audio_path = download_audio(youtube_url)
    transcript = transcribe_audio(audio_path)
    summary = summarize_text(transcript)
    return summary

if __name__ == "__main__":
    url = input("Enter YouTube URL: ").strip()
    result = summarize_youtube_video(url)
    print("\n--- SUMMARY ---\n")
    print(result)
