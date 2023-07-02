import streamlit as st

from helpers import switch_page
from style import CSS
import logging

from streamlit_option_menu import option_menu

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


def header(logo_and_title=True):
    if "first_run" not in st.session_state:
        st.session_state.first_run = True
        for key in [
            "search_results",
            "selected_value",
            "filename",
            "executed",
            "play_karaoke",
            "url",
            "random_song",
            "last_dir",
        ]:
            st.session_state[key] = None
        st.session_state.video_options = []
        st.session_state.page = "Karaoke"
        switch_page(st.session_state.page)

    st.set_page_config(
        page_title="Moseca - Music Separation and Karaoke - Free and Open Source alternative to lalal.ai, splitter.ai or media.io vocal remover.",
        page_icon="img/logo_moseca.png",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    options = ["Karaoke", "Separate", "About"]
    page = option_menu(
        menu_title=None,
        options=options,
        # bootrap icons
        icons=["play-btn-fill", "file-earmark-music", "info-circle"],
        default_index=options.index(st.session_state.page),
        orientation="horizontal",
        styles={"nav-link": {"padding-left": "1.5rem", "padding-right": "1.5rem"}},
        key="",
    )
    if page != st.session_state.page:
        switch_page(page)

    if logo_and_title:
        head = st.columns([5, 1, 3, 5])
        with head[1]:
            st.image("img/logo_moseca.png", use_column_width=False, width=80)
        with head[2]:
            st.markdown(
                "<h1>moseca</h1><p><b>Music Source Separation & Karaoke</b></p>",
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    header()
