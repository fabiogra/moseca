from pydub import AudioSegment

import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

@st.cache_data
def load_audio_segment(path: str, format: str) -> AudioSegment:
    return AudioSegment.from_file(path, format=format)

def plot_audio(_audio_segment: AudioSegment, title: str = None) -> go.Figure:
    samples = _audio_segment.get_array_of_samples()
    arr = np.array(samples[::20])
    df = pd.DataFrame(arr)
    fig = px.line(df, y=0, render_mode="webgl", line_shape="linear", width=1000, height=60, title=title)
    fig.update_layout(xaxis_fixedrange=True, yaxis_fixedrange=True, yaxis_visible=False, xaxis_visible=False, hovermode=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
