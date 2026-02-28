#!/usr/bin/env python3
"""Moseca - Music Source Separation powered by Facebook Research DEMUCS."""

import os
import time
from pathlib import Path
from typing import Optional

import gradio as gr
import requests
from loguru import logger as log
from pydub import AudioSegment

from app.service.demucs_runner import separator

# ── Constants ─────────────────────────────────────────────────────────────────

LABEL_SOURCES = {
    "vocals.mp3": "🎤 Vocals",
    "no_vocals.mp3": "🎶 Instrumental",
    "drums.mp3": "🥁 Drums",
    "bass.mp3": "🎸 Bass",
    "guitar.mp3": "🎸 Guitar",
    "piano.mp3": "🎹 Piano",
    "other.mp3": "🎶 Other",
}

SEPARATION_MODES = {
    "Vocals & Instrumental": {
        "model": "htdemucs",
        "stem": "vocals",
        "stems": ["vocals.mp3", "no_vocals.mp3"],
    },
    "Vocals, Drums, Bass & Other (4 stems)": {
        "model": "htdemucs",
        "stem": None,
        "stems": ["vocals.mp3", "drums.mp3", "bass.mp3", "other.mp3"],
    },
    "Vocals, Drums, Bass, Guitar, Piano & Other (6 stems)": {
        "model": "htdemucs_6s",
        "stem": None,
        "stems": ["vocals.mp3", "drums.mp3", "bass.mp3", "guitar.mp3", "piano.mp3", "other.mp3"],
    },
}

MAX_STEMS = 6  # Maximum stems across all modes (htdemucs_6s)
MAX_DURATION = 15  # Max seconds when ENV_LIMITATION is set
IN_PATH = Path("/tmp")
OUT_PATH = Path("/tmp")
SUPPORTED_EXTENSIONS = {"mp3", "wav", "ogg", "flac"}

# ── Helpers ───────────────────────────────────────────────────────────────────


def _remove_file_older_than(file_path: str, max_age_limit: float) -> None:
    if os.path.getmtime(file_path) < max_age_limit:
        try:
            log.info(f"Deleting old file: {file_path}")
            os.remove(file_path)
        except OSError as e:
            log.warning(f"Could not delete {file_path}: {e.strerror}")


def delete_old_files(directory: str, age_limit_seconds: int) -> None:
    """Remove files older than age_limit_seconds from directory tree."""
    age_limit = time.time() - age_limit_seconds
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            _remove_file_older_than(file_path, age_limit)


# ── Core separation function ──────────────────────────────────────────────────


def separate_music(
    audio_file: Optional[str],
    url: str,
    separation_mode: str,
    start_time: int,
    progress=gr.Progress(track_tqdm=True),
) -> list:
    """Separate audio into stems using DEMUCS.

    Returns a list of MAX_STEMS gr.update() dicts — one per audio output component.
    Active stems get value + visible=True; unused ones get visible=False.
    """
    if audio_file is None and not (url and url.strip()):
        raise gr.Error("Please upload an audio file or provide a URL.")

    mode_config = SEPARATION_MODES[separation_mode]
    model_name = mode_config["model"]
    stem = mode_config["stem"]
    file_sources = mode_config["stems"]
    stem_labels = [LABEL_SOURCES.get(s, s) for s in file_sources]

    # ── Download from URL if no file was uploaded ──────────────────────────
    if audio_file is None:
        url = url.strip()
        # Extract extension, stripping any query string
        raw_ext = url.split(".")[-1].lower().split("?")[0]
        if raw_ext not in SUPPORTED_EXTENSIONS:
            raise gr.Error(
                f"Unsupported audio format '{raw_ext}'. Please use: {', '.join(SUPPORTED_EXTENSIONS)}."
            )
        filename = f"input_{int(time.time())}.{raw_ext}"
        filepath = IN_PATH / filename
        progress(0.05, desc="Downloading audio from URL…")
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            audio_file = str(filepath)
        except Exception as exc:
            raise gr.Error(f"Failed to download audio: {exc}") from exc

    track_path = Path(audio_file)

    # ── Apply duration limit when ENV_LIMITATION is set ───────────────────
    if os.environ.get("ENV_LIMITATION"):
        try:
            ext = track_path.suffix.lstrip(".")
            audio_seg = AudioSegment.from_file(str(track_path), format=ext)
            n_secs = len(audio_seg) // 1000
            effective_start = max(0, min(start_time, n_secs - 1))
            end_secs = min(effective_start + MAX_DURATION, n_secs)
            sliced = audio_seg[effective_start * 1000 : end_secs * 1000]
            sliced_name = f"sliced_{track_path.stem}_{effective_start}_{end_secs}{track_path.suffix}"
            sliced_path = IN_PATH / sliced_name
            sliced.export(str(sliced_path), format=ext)
            track_path = sliced_path
            log.info(f"Audio sliced: {effective_start}s → {end_secs}s ({track_path.name})")
        except Exception as exc:
            log.warning(f"Could not apply duration limit, using full file: {exc}")

    progress(0.15, desc=f"Running {model_name} separation…")
    log.info(f"Separating '{track_path.name}' — model={model_name}, stem={stem}")

    try:
        separator(
            tracks=[track_path],
            out=OUT_PATH,
            model=model_name,
            shifts=1,
            overlap=0.5,
            stem=stem,
            int24=False,
            float32=False,
            clip_mode="rescale",
            mp3=True,
            mp3_bitrate=320,
            verbose=False,
        )
    except Exception as exc:
        log.error(f"Separation failed: {exc}")
        raise gr.Error(f"Separation failed: {exc}") from exc

    dir_name = track_path.stem
    output_dir = OUT_PATH / model_name / dir_name

    # Build one gr.update() per MAX_STEMS output slot
    results = []
    for i in range(MAX_STEMS):
        if i < len(file_sources):
            source_path = output_dir / file_sources[i]
            if source_path.exists():
                results.append(
                    gr.update(value=str(source_path), visible=True, label=stem_labels[i])
                )
            else:
                results.append(gr.update(value=None, visible=False, label=f"Stem {i + 1}"))
        else:
            results.append(gr.update(value=None, visible=False, label=f"Stem {i + 1}"))

    log.info(f"Separation complete: {dir_name} → {model_name}")
    delete_old_files(str(OUT_PATH), age_limit_seconds=60 * 30)
    return results


# ── Gradio UI ─────────────────────────────────────────────────────────────────

CSS = """
#header { text-align: center; padding: 1.5rem 0 0.5rem 0; }
#header h1 { font-size: 3rem; font-weight: 800; margin-bottom: 0.1rem; }
#header p  { font-size: 1.1rem; color: #6b7280; margin-top: 0; }
.stem-audio { margin-top: 0.4rem; }
"""

with gr.Blocks(
    title="Moseca — Music Source Separation",
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="purple"),
    css=CSS,
) as demo:

    gr.Markdown(
        """
        <div id="header">
          <h1>🎵 moseca</h1>
          <p><strong>Music Source Separation</strong> — Free &amp; Open Source<br>
          Powered by <a href="https://github.com/facebookresearch/demucs" target="_blank">
          Facebook Research DEMUCS</a></p>
        </div>
        """,
    )

    with gr.Tabs():

        # ── Separate ──────────────────────────────────────────────────────
        with gr.TabItem("🎶 Separate"):
            with gr.Row(equal_height=False):

                # Left: inputs
                with gr.Column(scale=1, min_width=320):
                    gr.Markdown("### Input")
                    audio_input = gr.Audio(
                        label="Upload Audio File (mp3, wav, ogg, flac)",
                        type="filepath",
                        sources=["upload"],
                    )
                    url_input = gr.Textbox(
                        label="Or paste a direct audio URL",
                        placeholder="https://example.com/song.mp3",
                    )
                    separation_mode = gr.Dropdown(
                        choices=list(SEPARATION_MODES.keys()),
                        value=list(SEPARATION_MODES.keys())[0],
                        label="Separation Mode",
                    )
                    start_time_slider = gr.Slider(
                        minimum=0,
                        maximum=300,
                        step=1,
                        value=0,
                        label=f"Start time (s) — up to {MAX_DURATION}s will be processed",
                        visible=bool(os.environ.get("ENV_LIMITATION")),
                        info="Only used when ENV_LIMITATION is enabled.",
                    )
                    with gr.Row():
                        clear_btn = gr.ClearButton(value="Clear", size="sm")
                        submit_btn = gr.Button("Separate 🎶", variant="primary", size="lg")

                # Right: outputs
                with gr.Column(scale=1, min_width=320):
                    gr.Markdown("### Separated Stems")
                    audio_outputs = []
                    for i in range(MAX_STEMS):
                        ao = gr.Audio(
                            label=f"Stem {i + 1}",
                            visible=False,
                            interactive=False,
                            elem_classes=["stem-audio"],
                        )
                        audio_outputs.append(ao)

            clear_btn.add([audio_input, url_input] + audio_outputs)

            submit_btn.click(
                fn=separate_music,
                inputs=[audio_input, url_input, separation_mode, start_time_slider],
                outputs=audio_outputs,
                concurrency_limit=1,
                concurrency_id="gpu_queue",
            )

        # ── About ─────────────────────────────────────────────────────────
        with gr.TabItem("ℹ️ About"):
            gr.Markdown(
                f"""
## About Moseca

**Moseca** (Music Source Separation) is a free, open-source web app that uses
state-of-the-art AI to split any song into individual stems — vocals, drums, bass,
guitar, piano, and more.

---

### Separation Modes

| Mode | Model | Output Stems |
|------|-------|:---:|
| Vocals & Instrumental | htdemucs | 2 |
| Vocals, Drums, Bass & Other | htdemucs | 4 |
| Vocals, Drums, Bass, Guitar, Piano & Other | htdemucs_6s | 6 |

### Models

All separation is powered by **[Facebook Research DEMUCS](https://github.com/facebookresearch/demucs)**
(Hybrid Transformer DEMUCS):

- **htdemucs** — Hybrid Transformer DEMUCS, state-of-the-art 4-stem model
- **htdemucs_6s** — Extended 6-stem variant with dedicated guitar and piano tracks

Both models run on **GPU** when available, automatically falling back to CPU.

### Queue System

This app runs on free HuggingFace Spaces resources. A built-in job queue ensures
fair access for all users — you'll see your position in the queue while waiting.
Processing typically takes **1–5 minutes** per song depending on length and mode.

### Resource Limits

When resource limits are enabled (`ENV_LIMITATION=true`):

- Only the first **{MAX_DURATION} seconds** from the chosen start time are processed.
- Use the *Start time* slider to select which segment to separate.
- [Duplicate this Space](https://huggingface.co/spaces/fabiogra/moseca) to remove any limit.

### Source Code

[github.com/fabiogra/moseca](https://github.com/fabiogra/moseca)
                """
            )


# ── Queue + Launch ────────────────────────────────────────────────────────────

demo.queue(max_size=20, default_concurrency_limit=1)
demo.launch(
    server_port=int(os.environ.get("PORT", 7860)),
    server_name="0.0.0.0",
    show_api=False,
)
