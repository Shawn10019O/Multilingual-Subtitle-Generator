import streamlit as st
import os
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random


def update_segments_text(segments, texts):
    for i, text in enumerate(texts):
        if i < len(segments):
            segments[i]["text"] = text
    return segments


def generate_subtitle_video(video_path, subtitles):

    video = VideoFileClip(video_path)
    subtitle_clips = []

    font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

    speaker_colors = {
        "SPEAKER_00": (255, 0, 0, 255),    
        "SPEAKER_01": (0, 255, 0, 255),   
        "SPEAKER_02": (0, 0, 255, 255),   
        "Unknown": (255, 255, 255, 255)   
    }

    progress_bar = st.progress(0)
    total_segments = len(subtitles)

    for i, seg in enumerate(subtitles):
        start, end, text = seg.get("start"), seg.get("end"), seg.get("text", "")
        speaker = seg.get("speaker", "Unknown")
        duration = end - start

        if speaker not in speaker_colors:
            speaker_colors[speaker] = (
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
                255
            )
        text_color = speaker_colors[speaker]

        max_font_size = 40
        min_font_size = 16
        font_size = max_font_size
        font = ImageFont.truetype(font_path, font_size)
        while font.getbbox(text)[2] > video.w - 40 and font_size > min_font_size:
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)

        img_height = 80
        img = Image.new('RGBA', (video.w, img_height), (0, 0, 0, 160))
        draw = ImageDraw.Draw(img)
        text_bbox = font.getbbox(text)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        draw.text(
            ((video.w - text_width) / 2, (img_height - text_height) / 2),
            text, fill=text_color, font=font
        )
        subtitle_img = ImageClip(np.array(img), duration=duration)
        subtitle_img = subtitle_img.set_position(('center', video.h - img_height - 20)).set_start(start)
        subtitle_clips.append(subtitle_img)

        progress_bar.progress((i + 1) / total_segments)

    final_video = CompositeVideoClip([video] + subtitle_clips)
    output_path = video_path.replace(".mp4", "_subtitled.mp4")
    final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
    progress_bar.empty()
    return output_path