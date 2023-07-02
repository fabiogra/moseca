import random
from io import BytesIO
import json

import matplotlib.pyplot as plt
import numpy as np
import requests
import streamlit as st
from PIL import Image
from pydub import AudioSegment
from base64 import b64encode
from pathlib import Path
from streamlit.runtime.scriptrunner import RerunData, RerunException
from streamlit.source_util import get_pages
from streamlit_player import st_player

extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.
example_songs = [1, 2, 3]


def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = b64encode(img_bytes).decode()
    return encoded


# @st.cache_data(show_spinner=False)
def img_to_html(img_path):
    img_html = "<div style='display: flex; justify-content: center; align-items: center; height: 50vh;'><img src='data:image/png;base64,{}' class='img-fluid' style='max-width: 100%; max-height: 100%;' ></div>".format(
        img_to_bytes(img_path)
    )
    return img_html


@st.cache_data(show_spinner=False)
def url_is_valid(url):
    if url.startswith("http") is False:
        st.error("URL should start with http or https.")
        return False
    elif url.split(".")[-1] not in extensions:
        st.error("Extension not supported.")
        return False
    try:
        r = requests.get(url)
        r.raise_for_status()
        return True
    except Exception:
        st.error("URL is not valid.")
        return False


@st.cache_data(show_spinner=False)
def load_audio_segment(path: str, format: str) -> AudioSegment:
    return AudioSegment.from_file(path, format=format)


@st.cache_data(show_spinner=False)
def plot_audio(_audio_segment: AudioSegment, *args, **kwargs) -> Image.Image:
    samples = _audio_segment.get_array_of_samples()
    arr = np.array(samples)

    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(arr, linewidth=0.05)
    ax.set_axis_off()

    # Set the background color to transparent
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    image = Image.open(buf)

    plt.close(fig)
    return image


def get_random_song():
    sample_songs = json.load(open("sample_songs.json"))
    name, url = random.choice(list(sample_songs.items()))
    return name, url


def streamlit_player(
    player,
    url,
    height,
    is_active,
    muted,
    start,
    key,
    playback_rate=1,
    events=None,
    play_inline=False,
    light=False,
):
    with player:
        options = {
            "progress_interval": 1000,
            "playing": is_active,  # st.checkbox("Playing", False),
            "muted": muted,
            "light": light,
            "play_inline": play_inline,
            "playback_rate": playback_rate,
            "height": height,
            "config": {"start": start},
            "events": events,
        }
        if url != "":
            events = st_player(url, **options, key=key)
    return events


@st.cache_data(show_spinner=False)
def local_audio(path, mime="audio/mp3"):
    data = b64encode(Path(path).read_bytes()).decode()
    return [{"type": mime, "src": f"data:{mime};base64,{data}"}]


def _standardize_name(name: str) -> str:
    return name.lower().replace("_", " ").strip()


@st.cache_data(show_spinner=False)
def switch_page(page_name: str):
    st.session_state.page = page_name

    page_name = _standardize_name(page_name)

    pages = get_pages("header.py")  # OR whatever your main page is called

    for page_hash, config in pages.items():
        if _standardize_name(config["page_name"]) == page_name:
            raise RerunException(
                RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )

    page_names = [_standardize_name(config["page_name"]) for config in pages.values()]
    raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")


def st_local_audio(pathname, key):
    st_player(
        local_audio(pathname),
        **{
            "progress_interval": 1000,
            "playing": False,
            "muted": False,
            "light": False,
            "play_inline": True,
            "playback_rate": 1,
            "height": 40,
            "config": {"start": 0, "forceAudio": True, "forceHLS": True, "forceSafariHLS": True},
        },
        key=key,
    )
