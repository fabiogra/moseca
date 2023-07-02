import os
from pathlib import Path

import streamlit as st
from streamlit_option_menu import option_menu

from service.demucs_runner import separator
from helpers import (
    load_audio_segment,
    plot_audio,
    st_local_audio,
    url_is_valid,
)

from service.vocal_remover.runner import separate, load_model

from footer import footer
from header import header

label_sources = {
    "no_vocals.mp3": "🎶 Instrumental",
    "vocals.mp3": "🎤 Vocals",
    "drums.mp3": "🥁 Drums",
    "bass.mp3": "🎸 Bass",
    "guitar.mp3": "🎸 Guitar",
    "piano.mp3": "🎹 Piano",
    "other.mp3": "🎶 Other",
}

extensions = ["mp3", "wav", "ogg", "flac"]


out_path = Path("/tmp")
in_path = Path("/tmp")


def reset_execution():
    st.session_state.executed = False


def body():
    filename = None
    cols = st.columns([1, 3, 2, 1])
    with cols[1]:
        with st.columns([1, 5, 1])[1]:
            option = option_menu(
                menu_title=None,
                options=["Upload File", "From URL"],
                icons=["cloud-upload-fill", "link-45deg"],
                orientation="horizontal",
                styles={"container": {"width": "100%", "margin": "0px", "padding": "0px"}},
                key="option_separate",
            )
        if option == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=extensions,
                key="file",
                help="Supported formats: mp3, wav, ogg, flac.",
            )
            if uploaded_file is not None:
                with open(in_path / uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                filename = uploaded_file.name
                st_local_audio(in_path / filename, key="input_upload_file")

        elif option == "From URL":  # TODO: show examples
            url = st.text_input(
                "Paste the URL of the audio file",
                key="url_input",
                help="Supported formats: mp3, wav, ogg, flac.",
            )
            if url != "":
                if url_is_valid(url):
                    with st.spinner("Downloading audio..."):
                        filename = url.split("/")[-1]
                        os.system(f"wget -O {in_path / filename} {url}")
                st_local_audio(in_path / filename, key="input_from_url")
    with cols[2]:
        separation_mode = st.selectbox(
            "Choose the separation mode",
            [
                "Vocals & Instrumental (Faster)",
                "Vocals & Instrumental (High Quality, Slower)",
                "Vocals, Drums, Bass & Other (Slower)",
                "Vocal, Drums, Bass, Guitar, Piano & Other (Slowest)",
            ],
            on_change=reset_execution(),
            key="separation_mode",
        )
        if separation_mode == "Vocals & Instrumental (Faster)":
            max_duration = 30
        else:
            max_duration = 15

    if filename is not None:
        song = load_audio_segment(in_path / filename, filename.split(".")[-1])
        n_secs = round(len(song) / 1000)
        if os.environ.get("ENV_LIMITATION", False):
            with cols[2]:
                start_time = st.number_input(
                    "Choose the start time",
                    min_value=0,
                    max_value=n_secs,
                    step=1,
                    value=0,
                    help=f"Maximum duration is {max_duration} seconds for this separation mode. Duplicate this space to remove any limit.",
                    format="%d",
                )
                st.session_state.start_time = start_time
                end_time = min(start_time + max_duration, n_secs)
                song = song[start_time * 1000 : end_time * 1000]
                st.info(
                    f"Audio source will be processed from {start_time} to {end_time} seconds. Duplicate this space to remove any limit.",
                    icon="⏱",
                )
        else:
            start_time = 0
            end_time = n_secs
        with st.columns([1, 3, 1])[1]:
            execute = st.button("Split Music 🎶", type="primary", use_container_width=True)
            if execute or st.session_state.executed:
                if execute:
                    st.session_state.executed = False

                if not st.session_state.executed:
                    song.export(in_path / filename, format=filename.split(".")[-1])
                    with st.spinner("Separating source audio, it will take a while..."):
                        if separation_mode == "Vocals & Instrumental (Faster)":
                            model_name = "vocal_remover"
                            model, device = load_model(pretrained_model="baseline.pth")
                            separate(
                                input=in_path / filename,
                                model=model,
                                device=device,
                                output_dir=out_path,
                            )
                        else:
                            stem = None
                            model_name = "htdemucs"
                            if (
                                separation_mode
                                == "Vocal, Drums, Bass, Guitar, Piano & Other (Slowest)"
                            ):
                                model_name = "htdemucs_6s"
                            elif separation_mode == "Vocals & Instrumental (High Quality, Slower)":
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
                last_dir = ".".join(filename.split(".")[:-1])
                filename = None
                st.session_state.executed = True

                def get_sources(path):
                    sources = {}
                    for file in [
                        "no_vocals.mp3",
                        "vocals.mp3",
                        "drums.mp3",
                        "bass.mp3",
                        "guitar.mp3",
                        "piano.mp3",
                        "other.mp3",
                    ]:
                        fullpath = path / file
                        if fullpath.exists():
                            sources[file] = fullpath
                    return sources

                sources = get_sources(out_path / Path(model_name) / last_dir)
                tab_sources = st.tabs([f"**{label_sources.get(k)}**" for k in sources.keys()])
                for i, (file, pathname) in enumerate(sources.items()):
                    with tab_sources[i]:
                        cols = st.columns(2)
                        with cols[0]:
                            auseg = load_audio_segment(pathname, "mp3")
                            st.image(
                                plot_audio(auseg, title="", file=file),
                                use_column_width="always",
                            )
                        with cols[1]:
                            st_local_audio(pathname, key=f"output_{file}")


if __name__ == "__main__":
    header()
    body()
    footer()
