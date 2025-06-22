import streamlit as st
from core.io import save_uploaded_file, extract_audio
from core.speech import (
    transcribe_audio,
    translate_text_openai,
    identify_speakers,
    get_most_overlapped_speaker
)
from core.video import update_segments_text, generate_subtitle_video

st.title("🎥 Video Transcription & Subtitle Generator (with Translation)")

uploaded_file = st.file_uploader("Please upload a video", type=["mp4", "mov", "avi"])
if uploaded_file:
    st.video(uploaded_file)
    video_path = save_uploaded_file(uploaded_file)
    audio_path = extract_audio(video_path)

    st.write("🎙 Transcribing audio...")
    transcript_text, segments = transcribe_audio(audio_path)

    transcript_lines = [seg["text"] for seg in segments]
    edited_transcription = st.text_area("📝 Edit the subtitles", "\n".join(transcript_lines), height=300)

    target_language = st.selectbox(
        "Select the language you want to translate into",
        ["English", "Français", "Español", "Deutsch", "Chinese","Japanese"]
    )
    language_map = {
        "English": "en",
        "Français": "fr",
        "Español": "es",
        "Deutsch": "de",
        "Chinese": "zh",
        "Japanese":"ja"
    }
    selected_language_code = language_map[target_language]

    subtitle_mode = st.radio("Choose subtitle type", ["Original language", "Translated subtitles"])

    if "translated_transcription" not in st.session_state:
        st.session_state.translated_transcription = ""

    if st.button("🌍 Apply Translation"):
        edited_lines = edited_transcription.split("\n")
        translated_lines = [translate_text_openai(text, selected_language_code) for text in edited_lines]
        st.success(f"✅ Displaying subtitles in {target_language}")
        segments = update_segments_text(segments, translated_lines)
        st.session_state.translated_transcription = "\n".join(translated_lines)

    if subtitle_mode == "Translated subtitles":
        final_transcription = st.text_area(
            "📝 Edit the translated subtitles",
            st.session_state.translated_transcription,
            height=300
        )
    else:
        final_transcription = edited_transcription

    if st.button("🎬 Generate video with subtitles"):
        final_lines = final_transcription.split("\n")
        segments = update_segments_text(segments, final_lines)
        st.write("🔊 Identifying speakers...")
        speaker_segments = identify_speakers(audio_path)
        for seg in segments:
            seg["speaker"] = get_most_overlapped_speaker(seg["start"], seg["end"], speaker_segments)
        subtitle_video_path = generate_subtitle_video(video_path, segments)
        st.success("🎉 Subtitle video generation completed!")
        st.video(subtitle_video_path)
        with open(subtitle_video_path, "rb") as f:
            st.download_button(
                "📥 Download the video with subtitles",
                data=f.read(),
                file_name="final_subtitled_video.mp4",
                mime="video/mp4"
            )
