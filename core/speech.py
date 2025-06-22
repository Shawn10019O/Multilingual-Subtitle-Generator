import streamlit as st
import whisper
import os
from pyannote.audio import Pipeline
from dotenv import load_dotenv
from openai import OpenAI


client = OpenAI()


load_dotenv()
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    st.warning("⚠ Hugging Face API token is not set! Please add HUGGINGFACE_API_TOKEN to your .env file.")


def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"], result["segments"]


def translate_text_openai(text, target_language="en"):
    prompt = f" Please translate the following text into {target_language}:\n{text}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()


def identify_speakers(audio_path):
    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        use_auth_token=HUGGINGFACE_API_TOKEN
    )
    diarization = pipeline(audio_path)
    speaker_segments = []
    for segment, _, speaker in diarization.itertracks(yield_label=True):
        speaker_segments.append((segment.start, segment.end, speaker))
    return speaker_segments


def compute_overlap(start1, end1, start2, end2):
    return max(0, min(end1, end2) - max(start1, start2))


def get_most_overlapped_speaker(ws_start, ws_end, diarization_segments):
  
    best_speaker = "Unknown"
    best_overlap = 0
    for ds_start, ds_end, ds_speaker in diarization_segments:
        overlap = compute_overlap(ws_start, ws_end, ds_start, ds_end)
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = ds_speaker
    return best_speaker