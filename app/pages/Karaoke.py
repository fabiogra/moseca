from pathlib import Path

import streamlit as st
from streamlit_player import st_player

from service.youtube import (
    get_youtube_url,
    search_youtube,
    download_audio_from_youtube,
)
from helpers import (
    get_random_song,
    load_audio_segment,
    streamlit_player,
    local_audio,
    delete_old_files,
)

from service.vocal_remover.runner import separate, load_model
from footer import footer
from header import header
from loguru import logger as log


out_path = Path("/tmp")
in_path = Path("/tmp")

sess = st.session_state


def show_karaoke(pathname):
    st.session_state.karaoke = True
    cols = st.columns([1, 1, 3, 1])
    with cols[1]:
        sess.delay = st.slider(
            label="Adjust video start delay in seconds (higher values anticipate lyrics, need to restart the player)",
            key="delay_slider",
            value=2,
            min_value=0,
            max_value=5,
            help="Synchronize youtube player with karaoke audio by adding a delay to the youtube player.",
        )
    with cols[2]:
        events = st_player(
            local_audio(pathname),
            **{
                "progress_interval": 1000,
                "playing": False,
                "muted": False,
                "light": False,
                "play_inline": True,
                "playback_rate": 1,
                "height": 40,
                "config": {
                    "start": 0,
                    "forceAudio": True,
                },
                "events": ["onProgress", "onPlay"],
            },
            key="karaoke_player",
        )
    st.markdown(
        """<center>⬆️ Click on the play button to start karaoke<br>You will see the video with lyrics below ⬇️<center>""",
        unsafe_allow_html=True,
    )
    with st.columns([1, 4, 1])[1]:
        if events.name == "onPlay":
            sess.player_restart = True
            log.info(f"Play Karaoke - {sess.selected_value} - {sess.delay}s delay")

        elif (
            events.name == "onProgress"
            and events.data["playedSeconds"] > 0
            and events.data["played"] < 1
        ):
            if sess.player_restart:
                sess.tot_delay = sess.delay + events.data["playedSeconds"]
                sess.player_restart = False
            st_player(
                sess.url + f"&t={sess.tot_delay}s",
                **{
                    "progress_interval": 1000,
                    "playing": True,
                    "muted": True,
                    "light": False,
                    "play_inline": False,
                    "playback_rate": 1,
                    "height": 250,
                    "events": None,
                },
                key="yt_muted_player",
            )


def reset_karaoke():
    sess.karaoke = False
    sess.url = None
    sess.executed = False


def body():
    st.markdown(
        "<h4><center>Play karaoke removing the vocals of your favorite song <center></h4>",
        unsafe_allow_html=True,
    )
    yt_cols = st.columns([1, 3, 2, 1])
    selected_value = None
    with yt_cols[1]:
        input_search = st.text_input(
            label="Search a song on YouTube",
            label_visibility="collapsed",
            placeholder="Search on YouTube by name...",
            key="yt_input_search",
            on_change=reset_karaoke,
        )
        radio_selection = st.empty()
        if not sess.get("karaoke", False):
            if input_search != "" and input_search != sess.get("input_search", ""):
                sess.input_search = input_search
                with st.spinner("Searching on YouTube..."):
                    sess.options = search_youtube(input_search)
            if sess.get("options", []) != []:
                selected_value = radio_selection.selectbox(
                    label="**⬇️ Select a title and see the video preview**",
                    index=len(sess.options),
                    options=sess.options + [""],
                    key="yt_radio",
                )

        if not sess.get("karaoke", False):
            if selected_value is not None and selected_value in sess.video_options:
                sess.random_song = None

                if selected_value != sess.selected_value:  # New song selected
                    sess.executed = False

                sess.selected_value = selected_value
                sess.url = get_youtube_url(selected_value)

    if selected_value is None or selected_value == "":
        with yt_cols[2]:
            if st.button("🎲 Random song", use_container_width=True):
                reset_karaoke()
                sess.last_dir, sess.url = get_random_song()
                log.info(f"Random song - {sess.last_dir}")
                sess.selected_value = sess.last_dir
                sess.random_song = True
                sess.video_options = []
                sess.executed = False
                radio_selection.empty()

    if sess.url is not None and not sess.get("karaoke", False):
        player_cols = st.columns([2, 2, 1, 1], gap="medium")
        with player_cols[1]:
            with st.spinner("Loading video preview..."):
                player = st.empty()
                streamlit_player(
                    player,
                    sess.url,
                    height=200,
                    is_active=False,
                    muted=False,
                    start=0,
                    key="yt_player",
                )

            # Separate vocals
            cols_before_sep = st.columns([2, 4, 2])
            with cols_before_sep[1]:
                execute_button = st.empty()
                execute = execute_button.button(
                    "Confirm and remove vocals 🎤 🎶",
                    type="primary",
                    use_container_width=True,
                )
            if execute or sess.executed:
                radio_selection.empty()
                execute_button.empty()
                player.empty()
                if execute:
                    sess.executed = False
                if sess.random_song is None:
                    if not sess.executed:
                        with st.spinner(
                            "Separating vocals from music, it could take a few minutes... Don't close this page!"
                        ):
                            log.info(f"Separating vocals from {sess.selected_value}")
                            sess.filename = download_audio_from_youtube(sess.url, in_path)
                            if sess.filename is None:
                                st.stop()
                            filename = sess.filename
                            song = load_audio_segment(in_path / filename, filename.split(".")[-1])
                            song.export(in_path / filename, format=filename.split(".")[-1])
                            model, device = load_model(pretrained_model="baseline.pth")
                            cancel_button = st.empty()
                            if cancel_button.button(
                                "Cancel", use_container_width=True, type="secondary"
                            ):
                                log.info(f"Cancel separation of vocals from {filename}")
                                st.experimental_rerun()
                            separate(
                                input=in_path / filename,
                                model=model,
                                device=device,
                                output_dir=out_path,
                                only_no_vocals=True,
                            )
                            selected_value = None
                            sess.last_dir = ".".join(sess.filename.split(".")[:-1])
                            sess.executed = True
                            cancel_button.empty()
                            log.info(f"Separating Done - {sess.selected_value}")

                else:
                    sess.executed = True

    if sess.executed:
        show_karaoke(out_path / "vocal_remover" / sess.last_dir / "no_vocals.mp3")


if __name__ == "__main__":
    header()
    body()
    footer()
    delete_old_files("/tmp", 60 * 30)
