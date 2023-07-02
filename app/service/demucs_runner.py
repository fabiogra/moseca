import argparse
import sys
from pathlib import Path
from typing import List
import os
from dora.log import fatal
import torch as th

from demucs.apply import apply_model, BagOfModels
from demucs.audio import save_audio
from demucs.pretrained import get_model_from_args, ModelLoadingError
from demucs.separate import load_track

import streamlit as st


@st.cache_data(show_spinner=False)
def separator(
    tracks: List[Path],
    out: Path,
    model: str,
    shifts: int,
    overlap: float,
    stem: str,
    int24: bool,
    float32: bool,
    clip_mode: str,
    mp3: bool,
    mp3_bitrate: int,
    verbose: bool,
    *args,
    **kwargs,
):
    """Separate the sources for the given tracks

    Args:
        tracks (Path): Path to tracks
        out (Path): Folder where to put extracted tracks. A subfolder with the model name will be
                    created.
        model (str): Model name
        shifts (int): Number of random shifts for equivariant stabilization.
                      Increase separation time but improves quality for Demucs.
                      10 was used in the original paper.
        overlap (float): Overlap
        stem (str): Only separate audio into {STEM} and no_{STEM}.
        int24 (bool): Save wav output as 24 bits wav.
        float32 (bool): Save wav output as float32 (2x bigger).
        clip_mode (str): Strategy for avoiding clipping: rescaling entire signal if necessary
                        (rescale) or hard clipping (clamp).
        mp3 (bool): Convert the output wavs to mp3.
        mp3_bitrate (int): Bitrate of converted mp3.
        verbose (bool): Verbose
    """

    if os.environ.get("LIMIT_CPU", False):
        th.set_num_threads(1)
        jobs = 1
    else:
        # Number of jobs. This can increase memory usage but will be much faster when
        # multiple cores are available.
        jobs = os.cpu_count()

    if th.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
    args = argparse.Namespace()
    args.tracks = tracks
    args.out = out
    args.model = model
    args.device = device
    args.shifts = shifts
    args.overlap = overlap
    args.stem = stem
    args.int24 = int24
    args.float32 = float32
    args.clip_mode = clip_mode
    args.mp3 = mp3
    args.mp3_bitrate = mp3_bitrate
    args.jobs = jobs
    args.verbose = verbose
    args.filename = "{track}/{stem}.{ext}"
    args.split = True
    args.segment = None
    args.name = model
    args.repo = None

    try:
        model = get_model_from_args(args)
    except ModelLoadingError as error:
        fatal(error.args[0])

    if args.segment is not None and args.segment < 8:
        fatal("Segment must greater than 8. ")

    if ".." in args.filename.replace("\\", "/").split("/"):
        fatal('".." must not appear in filename. ')

    if isinstance(model, BagOfModels):
        print(
            f"Selected model is a bag of {len(model.models)} models. "
            "You will see that many progress bars per track."
        )
        if args.segment is not None:
            for sub in model.models:
                sub.segment = args.segment
    else:
        if args.segment is not None:
            model.segment = args.segment

    model.cpu()
    model.eval()

    if args.stem is not None and args.stem not in model.sources:
        fatal(
            'error: stem "{stem}" is not in selected model. STEM must be one of {sources}.'.format(
                stem=args.stem, sources=", ".join(model.sources)
            )
        )
    out = args.out / args.name
    out.mkdir(parents=True, exist_ok=True)
    print(f"Separated tracks will be stored in {out.resolve()}")
    for track in args.tracks:
        if not track.exists():
            print(
                f"File {track} does not exist. If the path contains spaces, "
                'please try again after surrounding the entire path with quotes "".',
                file=sys.stderr,
            )
            continue
        print(f"Separating track {track}")
        wav = load_track(track, model.audio_channels, model.samplerate)

        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        sources = apply_model(
            model,
            wav[None],
            device=args.device,
            shifts=args.shifts,
            split=args.split,
            overlap=args.overlap,
            progress=True,
            num_workers=args.jobs,
        )[0]
        sources = sources * ref.std() + ref.mean()

        if args.mp3:
            ext = "mp3"
        else:
            ext = "wav"
        kwargs = {
            "samplerate": model.samplerate,
            "bitrate": args.mp3_bitrate,
            "clip": args.clip_mode,
            "as_float": args.float32,
            "bits_per_sample": 24 if args.int24 else 16,
        }
        if args.stem is None:
            for source, name in zip(sources, model.sources):
                stem = out / args.filename.format(
                    track=track.name.rsplit(".", 1)[0],
                    trackext=track.name.rsplit(".", 1)[-1],
                    stem=name,
                    ext=ext,
                )
                stem.parent.mkdir(parents=True, exist_ok=True)
                save_audio(source, str(stem), **kwargs)
        else:
            sources = list(sources)
            stem = out / args.filename.format(
                track=track.name.rsplit(".", 1)[0],
                trackext=track.name.rsplit(".", 1)[-1],
                stem=args.stem,
                ext=ext,
            )
            stem.parent.mkdir(parents=True, exist_ok=True)
            save_audio(sources.pop(model.sources.index(args.stem)), str(stem), **kwargs)
            # Warning : after poping the stem, selected stem is no longer in the list 'sources'
            other_stem = th.zeros_like(sources[0])
            for i in sources:
                other_stem += i
            stem = out / args.filename.format(
                track=track.name.rsplit(".", 1)[0],
                trackext=track.name.rsplit(".", 1)[-1],
                stem="no_" + args.stem,
                ext=ext,
            )
            stem.parent.mkdir(parents=True, exist_ok=True)
            save_audio(other_stem, str(stem), **kwargs)
