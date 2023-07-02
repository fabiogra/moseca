from pathlib import Path

import streamlit as st
from streamlit_player import st_player
from streamlit_searchbox import st_searchbox

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
)

from service.vocal_remover.runner import separate, load_model
from footer import footer
from header import header


out_path = Path("/tmp")
in_path = Path("/tmp")

sess = st.session_state


def show_karaoke(pathname, initial_player):
    cols = st.columns([1, 1, 3, 1])
    with cols[1]:
        sess.delay = st.slider(
            label="Start delay in karaoke (seconds)",
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
        "<center>⬆️ Click on the play button to start karaoke<center>",
        unsafe_allow_html=True,
    )
    with st.columns([1, 4, 1])[1]:
        if events.name == "onProgress" and events.data["playedSeconds"] > 0:
            initial_player.empty()
            st_player(
                sess.url + f"&t={sess.delay}s",
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


def body():
    st.markdown("<center>Search for a song on YouTube<center>", unsafe_allow_html=True)
    yt_cols = st.columns([1, 3, 2, 1])
    with yt_cols[1]:
        selected_value = st_searchbox(
            search_youtube,
            label=None,
            placeholder="Search by name...",
            clear_on_submit=True,
            key="yt_searchbox",
        )
        if selected_value is not None and selected_value in sess.video_options:
            sess.random_song = None

            if selected_value != sess.selected_value:  # New song selected
                sess.executed = False

            sess.selected_value = selected_value
            sess.url = get_youtube_url(selected_value)

    with yt_cols[2]:
        if st.button("🎲 Random song", use_container_width=True):
            sess.last_dir, sess.url = get_random_song()
            sess.random_song = True
            sess.video_options = []
            sess.executed = False

    if sess.url is not None:
        player_cols = st.columns([2, 2, 1, 1], gap="medium")
        with player_cols[1]:
            player = st.empty()
            streamlit_player(
                player,
                sess.url,
                height=200,
                is_active=False,
                muted=False,
                start=0,
                key="yt_player",
                events=["onProgress"],
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
                execute_button.empty()
                player.empty()
                if execute:
                    sess.executed = False
                if sess.random_song is None:
                    if not sess.executed:
                        cols_spinners = st.columns([1, 2, 1])
                        with cols_spinners[1]:
                            with st.spinner(
                                "Separating vocals from music, it will take a while..."
                            ):
                                sess.filename = download_audio_from_youtube(sess.url, in_path)
                                if sess.filename is None:
                                    st.stop()
                                sess.url = None
                                filename = sess.filename
                                song = load_audio_segment(
                                    in_path / filename, filename.split(".")[-1]
                                )
                                song.export(in_path / filename, format=filename.split(".")[-1])
                                model, device = load_model(pretrained_model="baseline.pth")
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
                else:
                    sess.executed = True

        if sess.executed:
            show_karaoke(out_path / "vocal_remover" / sess.last_dir / "no_vocals.mp3", player)


if __name__ == "__main__":
    header()
    body()
    footer()
