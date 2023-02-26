import logging
import os
from pathlib import Path
from shutil import rmtree

from pydub import AudioSegment
import streamlit as st

# from lib.st_custom_components import st_audiorec

try:
    from app.demucs_runner import separator
except ImportError:
    from demucs_runner import separator


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d %H:%M:%S",
)

max_duration = 10  # in seconds

model = "htdemucs"
extensions = ["mp3", "wav", "ogg", "flac"]  # we will look for all those file types.
two_stems = None   # only separate one stems from the rest, for instance

# Options for the output audio.
mp3 = True
mp3_rate = 320
float32 = False  # output as float 32 wavs, unsused if 'mp3' is True.
int24 = False  # output as int24 wavs, unused if 'mp3' is True.
# You cannot set both `float32 = True` and `int24 = True` !!


def find_files(in_path):
    out = []
    for file in Path(in_path).iterdir():
        if file.suffix.lower().lstrip(".") in extensions:
            out.append(file)
    return out

out_path = Path("separated")
in_path = Path("tmp_in")

def clean_folders():
    if in_path.exists():
        rmtree(in_path)
    in_path.mkdir()
    if out_path.exists():
        rmtree(out_path)
    out_path.mkdir()
    
def url_is_valid(url):
    import requests
    try:
        r = requests.get(url)
        r.raise_for_status()
        return True
    except Exception:
        st.error("URL is not valid.")


def run():
    st.markdown("<h1><center>🎶 Music Source Splitter</center></h1>", unsafe_allow_html=True)

    st.markdown("""
                <style>
                .st-af {
                    font-size: 1.5rem;
                    align-items: center;
                    padding-right: 2rem;
                }
                
                </style>
                """,
                unsafe_allow_html=True,
    )
    filename = None
    choice =  st.radio(label=" ", options=["🔗 From URL", "⬆️ Upload File", "🎤 Record Audio"], horizontal=True)
    if choice == "🔗 From URL":
        url = st.text_input("Paste the URL of the audio file", key="url")
        if url != "":
            # check if the url is valid
            if url_is_valid(url):
                with st.spinner("Downloading audio..."):
                    clean_folders()
                    filename = url.split("/")[-1]
                    os.system(f"wget -O {in_path / filename} {url}")
            
    elif choice == "⬆️ Upload File":
        uploaded_file = st.file_uploader("Choose a file")
        if uploaded_file is not None:
            clean_folders()
            with open(in_path / uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())    
            filename = uploaded_file.name        
    elif choice == "🎤 Record Audio":
        # wav_audio_data = st_audiorec()
        # if wav_audio_data is not None:
        #     if wav_audio_data != b'RIFF,\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x02\x00\x80>\x00\x00\x00\xfa\x00\x00\x04\x00\x10\x00data\x00\x00\x00\x00':
        #         clean_folders()
        #         filename = "recording.wav"
        #         with open(in_path / filename, "wb") as f:
        #             f.write(wav_audio_data)
        pass
                
    if filename is not None:
        st.markdown("<hr>", unsafe_allow_html=True)
        cols = st.columns(2)
        with cols[0]:
            st.markdown("<h3>Original Audio</h3>", unsafe_allow_html=True)
        with cols[1]:
            audio_file = open(in_path / filename, "rb")
            audio_bytes = audio_file.read()
            _ = st.audio(audio_bytes)
        
        song = AudioSegment.from_file(in_path / filename, filename.split(".")[-1])
        n_secs = round(len(song) / 1000)
        start_time = st.slider("Choose the start time", min_value=0, max_value=n_secs, value=0, help=f"Maximum duration is {max_duration} seconds.")
        end_time = min(start_time + max_duration, n_secs)
        tot_time = end_time - start_time
        st.info(f"Audio source will be processed from {start_time} to {end_time} seconds.", icon="⏱")
         
        execute = st.button("Split Music 🎶", type="primary")
        if execute:
            song = song[start_time*1000:end_time*1000]
            song.export(in_path / filename, format=filename.split(".")[-1])
            with st.spinner(f"Splitting source audio, it will take almost {round(tot_time*3.6)} seconds..."):
                separator(
                    tracks=[in_path / filename],
                    out=out_path,
                    model=model,
                    device="cpu",
                    shifts=1,
                    overlap=0.5,
                    stem=two_stems,
                    int24=int24,
                    float32=float32,
                    clip_mode="rescale",
                    mp3=mp3,
                    mp3_bitrate=mp3_rate,
                    jobs=os.cpu_count(),
                    verbose=True,
                )
                pass
            last_dir = ".".join(filename.split(".")[:-1])
            for file in ["vocals.mp3", "drums.mp3", "bass.mp3", "other.mp3"]:
                file = out_path / Path(model) / last_dir / file
                st.markdown("<hr>", unsafe_allow_html=True)
                cols = st.columns(2)
                with cols[0]:
                    label = file.name.split(".")[0].replace("_", " ").capitalize()
                    # add emoji to label
                    label = {
                        "Drums": "🥁",
                        "Bass": "🎸",
                        "Other": "🎹",
                        "Vocals": "🎤",
                    }.get(label) + " " + label
                    st.markdown("<h3>" + label + "</h3>", unsafe_allow_html=True)
                with cols[1]:
                    audio_file = open(file, "rb")
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes)
                    
if __name__ == "__main__":
    run()