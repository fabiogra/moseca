import os
from pathlib import Path
from typing import List
from loguru import logger as log

import requests
import streamlit as st
from streamlit_option_menu import option_menu

from footer import footer
from header import header
from helpers import (
    load_audio_segment,
    load_list_of_songs,
    plot_audio,
    url_is_valid,
    file_size_is_valid,
    delete_old_files,
)
from service.demucs_runner import separator
from service.vocal_remover.runner import load_model, separate
from style import CSS_TABS


label_sources = {
    "no_vocals.mp3": "🎶 Instrumental",
    "vocals.mp3": "🎤 Vocals",
    "drums.mp3": "🥁 Drums",
    "bass.mp3": "🎸 Bass",
    "guitar.mp3": "🎸 Guitar",
    "piano.mp3": "🎹 Piano",
    "other.mp3": "🎶 Other",
}

separation_mode_to_model = {
    "Vocals & Instrumental (Low Quality, Faster)": (
        "vocal_remover",
        ["vocals.mp3", "no_vocals.mp3"],
    ),
    "Vocals & Instrumental (High Quality, Slower)": ("htdemucs", ["vocals.mp3", "no_vocals.mp3"]),
    "Vocals, Drums, Bass & Other (Slower)": (
        "htdemucs",
        ["vocals.mp3", "drums.mp3", "bass.mp3", "other.mp3"],
    ),
    "Vocal, Drums, Bass, Guitar, Piano & Other (Slowest)": (
        "htdemucs_6s",
        ["vocals.mp3", "drums.mp3", "bass.mp3", "guitar.mp3", "piano.mp3", "other.mp3"],
    ),
}

extensions = ["mp3", "wav", "ogg", "flac"]

out_path = Path("/tmp")
in_path = Path("/tmp")


@st.cache_data(show_spinner=False)
def get_sources(path, file_sources):
    sources = {}
    for file in file_sources:
        fullpath = path / file
        if fullpath.exists():
            sources[file] = fullpath
    return sources


def reset_execution():
    st.session_state.executed = False


def show_results(model_name: str, dir_name_output: str, file_sources: List):
    sources = get_sources(out_path / Path(model_name) / dir_name_output, file_sources)
    tab_sources = st.tabs([f"**{label_sources.get(k)}**" for k in sources.keys()])
    for i, (file, pathname) in enumerate(sources.items()):
        with tab_sources[i]:
            cols = st.columns(2)
            with cols[0]:
                auseg = load_audio_segment(pathname, "mp3")
                st.image(
                    plot_audio(
                        auseg,
                        32767,
                        file=file,
                        model_name=model_name,
                        dir_name_output=dir_name_output,
                    ),
                    use_column_width="always",
                )
            with cols[1]:
                st.audio(str(pathname))
    log.info(f"Displaying results for {dir_name_output} - {model_name}")


def body():
    filename = None
    name_song = None
    st.markdown(
        "<h4><center>Extract Vocals & Instrumental from any song</center></h4>",
        unsafe_allow_html=True,
    )
    st.markdown(CSS_TABS, unsafe_allow_html=True)

    cols = st.columns([1, 4, 1, 3, 1])

    with cols[1]:
        with st.columns([1, 8, 1])[1]:
            option = option_menu(
                menu_title=None,
                options=["Examples", "Upload File", "From URL"],
                icons=["cloud-upload-fill", "link-45deg", "music-note-list"],
                orientation="horizontal",
                styles={
                    "container": {
                        "width": "100%",
                        "height": "3.5rem",
                        "margin": "0px",
                        "padding": "0px",
                    },
                    "icon": {"font-size": "1rem"},
                    "nav-link": {
                        "display": "flex",
                        "height": "3rem",
                        "justify-content": "center",
                        "align-items": "center",
                        "text-align": "center",
                        "flex-direction": "column",
                        "font-size": "1rem",
                        "padding-left": "0px",
                        "padding-right": "0px",
                    },
                },
                key="option_separate",
            )
        if option == "Examples":
            samples_song = load_list_of_songs(path="separate_songs.json")
            if samples_song is not None:
                name_song = st.selectbox(
                    label="Select a sample song and listen to sources separated",
                    options=list(samples_song.keys()) + [""],
                    format_func=lambda x: x.replace("_", " "),
                    index=len(samples_song),
                    key="select_example",
                )
                full_path = f"{in_path}/{name_song}"
                if name_song != "" and Path(full_path).exists():
                    st.audio(full_path)
                else:
                    name_song = None

        elif option == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=extensions,
                key="file",
                help="Supported formats: mp3, wav, ogg, flac.",
            )
            if uploaded_file is not None:
                with st.spinner("Loading audio..."):
                    with open(in_path / uploaded_file.name, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    filename = uploaded_file.name
                    st.audio(uploaded_file)

        elif option == "From URL":
            url = st.text_input(
                "Paste the URL of the audio file",
                key="url_input",
                help="Supported formats: mp3, wav, ogg, flac.",
            )

            if url != "" and url_is_valid(url):
                with st.spinner("Downloading audio..."):
                    filename = url.split("/")[-1]
                    response = requests.get(url, stream=True)
                    if response.status_code == 200 and file_size_is_valid(
                        response.headers.get("Content-Length")
                    ):
                        file_size = 0
                        with open(in_path / filename, "wb") as audio_file:
                            for chunk in response.iter_content(chunk_size=1024):
                                if chunk:
                                    audio_file.write(chunk)
                                    file_size += len(chunk)
                                    if not file_size_is_valid(file_size):
                                        audio_file.close()
                                        os.remove(in_path / filename)
                                        filename = None
                                        return
                        st.audio(f"{in_path}/{filename}")
                    else:
                        st.error(
                            "Failed to download audio file. Try to download it manually and upload it."
                        )
                        filename = None

    with cols[3]:
        separation_mode = st.selectbox(
            "Choose the separation mode",
            [
                "Vocals & Instrumental (Low Quality, Faster)",
                "Vocals & Instrumental (High Quality, Slower)",
                "Vocals, Drums, Bass & Other (Slower)",
                "Vocal, Drums, Bass, Guitar, Piano & Other (Slowest)",
            ],
            on_change=reset_execution(),
            key="separation_mode",
        )
        if separation_mode == "Vocals & Instrumental (Low Quality, Faster)":
            max_duration = 30
        else:
            max_duration = 15
        model_name, file_sources = separation_mode_to_model[separation_mode]

    if filename is not None:
        song = load_audio_segment(in_path / filename, filename.split(".")[-1])
        n_secs = round(len(song) / 1000)
        if os.environ.get("ENV_LIMITATION", False):
            with cols[3]:
                start_time = st.number_input(
                    "Choose the start time",
                    min_value=0,
                    max_value=n_secs,
                    step=1,
                    value=0,
                    help=f"Maximum duration is {max_duration} seconds for this separation mode.\nDuplicate this space to [remove any limit](https://github.com/fabiogra/moseca#are-there-any-limitations).",
                    format="%d",
                )
                st.session_state.start_time = start_time
                end_time = min(start_time + max_duration, n_secs)
                song = song[start_time * 1000 : end_time * 1000]
                st.info(
                    f"Audio source will be processed from {start_time} to {end_time} seconds.\nDuplicate this space to [remove any limit](https://github.com/fabiogra/moseca#are-there-any-limitations).",
                    icon="⏱",
                )
        else:
            start_time = 0
            end_time = n_secs
        with st.columns([2, 1, 2])[1]:
            execute = st.button(
                "Separate Music Sources 🎶", type="primary", use_container_width=True
            )
        if execute or st.session_state.executed:
            if execute:
                st.session_state.executed = False

            if not st.session_state.executed:
                log.info(f"{option} - Separating {filename} with {separation_mode}...")
                song.export(in_path / filename, format=filename.split(".")[-1])
                with st.columns([1, 1, 1])[1]:
                    with st.spinner("Separating source audio, it will take a while..."):
                        if model_name == "vocal_remover":
                            model, device = load_model(pretrained_model="baseline.pth")
                            separate(
                                input=in_path / filename,
                                model=model,
                                device=device,
                                output_dir=out_path,
                            )
                        else:
                            stem = None
                            if separation_mode == "Vocals & Instrumental (High Quality, Slower)":
                                stem = "vocals"

                            separator(
                                tracks=[in_path / filename],
                                out=out_path,
                                model=model_name,
                                shifts=1,
                                overlap=0.5,
                                stem=stem,
                                int24=False,
                                float32=False,
                                clip_mode="rescale",
                                mp3=True,
                                mp3_bitrate=320,
                                verbose=True,
                                start_time=start_time,
                                end_time=end_time,
                            )
            dir_name_output = ".".join(filename.split(".")[:-1])
            filename = None
            st.session_state.executed = True
            show_results(model_name, dir_name_output, file_sources)
    elif name_song is not None and option == "Examples":
        show_results(model_name, name_song, file_sources)


if __name__ == "__main__":
    header()
    body()
    footer()
    delete_old_files("/tmp", 60 * 30)
