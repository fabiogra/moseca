import os
from typing import List
import yt_dlp
import string
import time
import re
import streamlit as st
from pytube import Search


def _sanitize_filename(filename):
    safe_chars = "-_.() %s%s" % (
        re.escape(string.ascii_letters),
        re.escape(string.digits),
    )
    safe_filename = re.sub(f"[^{safe_chars}]", "_", filename)
    return safe_filename.strip()


@st.cache_data(show_spinner=False)
def download_audio_from_youtube(url, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(url, download=False)
    if info_dict.get("duration") > 360:
        st.error("Song is too long. Please use a song no longer than 6 minutes.")
        return
    video_title = info_dict.get("title", None)
    video_title = _sanitize_filename(video_title)
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.join(output_path, video_title),
        #'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return f"{video_title}.mp3"


@st.cache_data(show_spinner=False)
def query_youtube(query: str) -> Search:
    return Search(query)


def search_youtube(query: str) -> List:
    if len(query) > 3:
        time.sleep(0.5)
        search = query_youtube(query + " lyrics")
        st.session_state.search_results = search.results
        video_options = [video.title for video in st.session_state.search_results]
        st.session_state.video_options = video_options
    else:
        video_options = []
    return video_options


def get_youtube_url(title: str) -> str:
    video = st.session_state.search_results[st.session_state.video_options.index(title)]
    return video.embed_url


def check_if_is_youtube_url(url: str) -> bool:
    return url.startswith("http")
