import streamlit as st
from loguru import logger as log
from streamlit_option_menu import option_menu

from helpers import switch_page
from style import CSS

DEFAULT_PAGE = "Separate"


def header(logo_and_title=True):
    if "first_run" not in st.session_state:
        st.session_state.first_run = True
        for key in [
            "selected_value",
            "filename",
            "executed",
            "play_karaoke",
            "url",
            "random_song",
            "last_dir",
            "player_restart",
        ]:
            st.session_state[key] = None
        st.session_state.video_options = []
        st.session_state.tot_delay = 0
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "page" not in st.session_state:
        switch_page(DEFAULT_PAGE)

    st.set_page_config(
        page_title="Moseca - Music Separation and Karaoke - Free and Open Source alternative to lalal.ai, splitter.ai or media.io vocal remover.",
        page_icon="img/logo_moseca.png",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    options = ["Separate", "Karaoke", "About"]

    page = option_menu(
        menu_title=None,
        options=options,
        # bootrap icons
        icons=["play-btn-fill", "file-earmark-music", "info-circle"],
        default_index=options.index(st.session_state.get("page", DEFAULT_PAGE)),
        orientation="horizontal",
        styles={"nav-link": {"padding-left": "1.5rem", "padding-right": "1.5rem"}},
        key="",
    )
    if page != st.session_state.get("page", DEFAULT_PAGE):
        log.info(f"Go to {page}")
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
