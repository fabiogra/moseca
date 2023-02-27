---
title: Music Splitter
emoji: 🎶
colorFrom: indigo
colorTo: yellow
sdk: docker
pinned: true
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Music Source Splitter 🎶
> Extract vocals, drums, bass, and other from a music track.

<a href="https://huggingface.co/spaces/fabiogra/st-music-splitter"><img src="https://img.shields.io/badge/🤗%20Hugging%20Face-Spaces-blue" alt="Hugging Face Spaces"></a>

![preview](preview.gif)

This is a streamlit demo of Music Source Splitter published in [HuggingFace](https://huggingface.co/spaces/fabiogra/st-music-splitter).


## Usage

You can use the demo [here](https://huggingface.co/spaces/fabiogra/st-music-splitter), or run it locally with:

```bash
streamlit run app.py
```
> **Note**: In order to run the demo locally, you need to install the dependencies with `pip install -r requirements.txt`.


## How it works

The app uses a pretrained model called Hybrid Spectrogram and Waveform Source Separation from <a href="https://github.com/facebookresearch/demucs">facebook/htdemucs</a>.


## Acknowledgements
 - HtDemucs model from  <a href="https://github.com/facebookresearch/demucs">facebook/htdemucs</a>
 - Streamlit Audio Recorder from <a href="https://github.com/stefanrmmr/streamlit_audio_recorder">stefanrmmr/streamlit_audio_recorder</a>