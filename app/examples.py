import streamlit as st

from app.helpers import load_audio_segment, plot_audio

def _load_example(name: str):
    st.markdown("<center><h3> Original </h3></center>", unsafe_allow_html=True)

    cols = st.columns(2)
    with cols[0]:
        auseg = load_audio_segment(f"samples/{name}", "mp3")
        plot_audio(auseg, step=50)
    with cols[1]:
        audio_file = open(f"samples/{name}", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes)
    
    for file in ["vocals.mp3", "drums.mp3", "bass.mp3", "other.mp3"]:
        st.markdown("<br>", unsafe_allow_html=True)
        label = file.split(".")[0].capitalize()
        label = {
            "Drums": "🥁",
            "Bass": "🎸",
            "Other": "🎹",
            "Vocals": "🎤",
        }.get(label)  + " " + label
        st.markdown("<center><h3>" + label + "</h3></center>", unsafe_allow_html=True)

        cols = st.columns(2)
        with cols[0]:
            auseg = load_audio_segment(f"samples/{name.split('.mp3')[0]}/{file}", "mp3")
            plot_audio(auseg, step=50)
        with cols[1]:
            audio_file = open(f"samples/{name.split('.mp3')[0]}/{file}", "rb")
            audio_bytes = audio_file.read()
            st.audio(audio_bytes)
    

def show_examples():
    with st.columns([2, 8, 1])[1]:
        selection = st.selectbox("Select an example music to quickly see results", ["Something About You - Marilyn Ford", "Broke Me - FASSounds", "Indie Rock"])
    if selection == "Broke Me - FASSounds":
        _load_example("broke-me-fassounds.mp3")
        link = "https://pixabay.com/users/fassounds-3433550/"
        st.markdown(
            f"""Music by <a href="{link}">FASSounds</a> from <a href="{link}">Pixabay</a>""",
            unsafe_allow_html=True)
    elif selection == "Indie Rock":
        _load_example("indie-rock.mp3")
        link = "https://pixabay.com/music/indie-rock-112771/"
        st.markdown(
            f"""Music by <a href="{link}">Music_Unlimited</a> from <a href="{link}">Pixabay</a>""",
            unsafe_allow_html=True)
    elif selection == "Something About You - Marilyn Ford":
        _load_example("something-about-you-marilyn-ford.mp3")
        link = "https://pixabay.com/music/rnb-something-about-you-marilyn-ford-135781/"
        st.markdown(
            f"""Music by <a href="{link}">Marilyn Ford</a> from <a href="{link}">Pixabay</a>""",
            unsafe_allow_html=True)
