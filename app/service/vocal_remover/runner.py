import os
import logging
import librosa
import numpy as np
import soundfile as sf
import torch
from stqdm import stqdm
import streamlit as st
from pydub import AudioSegment

from app.service.vocal_remover import nets


if os.environ.get("LIMIT_CPU", False):
    torch.set_num_threads(1)


def merge_artifacts(y_mask, thres=0.05, min_range=64, fade_size=32):
    if min_range < fade_size * 2:
        raise ValueError("min_range must be >= fade_size * 2")

    idx = np.where(y_mask.min(axis=(0, 1)) > thres)[0]
    start_idx = np.insert(idx[np.where(np.diff(idx) != 1)[0] + 1], 0, idx[0])
    end_idx = np.append(idx[np.where(np.diff(idx) != 1)[0]], idx[-1])
    artifact_idx = np.where(end_idx - start_idx > min_range)[0]
    weight = np.zeros_like(y_mask)
    if len(artifact_idx) > 0:
        start_idx = start_idx[artifact_idx]
        end_idx = end_idx[artifact_idx]
        old_e = None
        for s, e in zip(start_idx, end_idx):
            if old_e is not None and s - old_e < fade_size:
                s = old_e - fade_size * 2

            if s != 0:
                weight[:, :, s : s + fade_size] = np.linspace(0, 1, fade_size)
            else:
                s -= fade_size

            if e != y_mask.shape[2]:
                weight[:, :, e - fade_size : e] = np.linspace(1, 0, fade_size)
            else:
                e += fade_size

            weight[:, :, s + fade_size : e - fade_size] = 1
            old_e = e

    v_mask = 1 - y_mask
    y_mask += weight * v_mask

    return y_mask


def make_padding(width, cropsize, offset):
    left = offset
    roi_size = cropsize - offset * 2
    if roi_size == 0:
        roi_size = cropsize
    right = roi_size - (width % roi_size) + left

    return left, right, roi_size


def wave_to_spectrogram(wave, hop_length, n_fft):
    wave_left = np.asfortranarray(wave[0])
    wave_right = np.asfortranarray(wave[1])

    spec_left = librosa.stft(wave_left, n_fft=n_fft, hop_length=hop_length)
    spec_right = librosa.stft(wave_right, n_fft=n_fft, hop_length=hop_length)
    spec = np.asfortranarray([spec_left, spec_right])

    return spec


def spectrogram_to_wave(spec, hop_length=1024):
    if spec.ndim == 2:
        wave = librosa.istft(spec, hop_length=hop_length)
    elif spec.ndim == 3:
        spec_left = np.asfortranarray(spec[0])
        spec_right = np.asfortranarray(spec[1])

        wave_left = librosa.istft(spec_left, hop_length=hop_length)
        wave_right = librosa.istft(spec_right, hop_length=hop_length)
        wave = np.asfortranarray([wave_left, wave_right])

    return wave


class Separator(object):
    def __init__(self, model, device, batchsize, cropsize, postprocess=False, progress_bar=None):
        self.model = model
        self.offset = model.offset
        self.device = device
        self.batchsize = batchsize
        self.cropsize = cropsize
        self.postprocess = postprocess
        self.progress_bar = progress_bar

    def _separate(self, X_mag_pad, roi_size):
        X_dataset = []
        patches = (X_mag_pad.shape[2] - 2 * self.offset) // roi_size
        for i in range(patches):
            start = i * roi_size
            X_mag_crop = X_mag_pad[:, :, start : start + self.cropsize]
            X_dataset.append(X_mag_crop)

        X_dataset = np.asarray(X_dataset)

        self.model.eval()
        with torch.no_grad():
            mask = []
            # To reduce the overhead, dataloader is not used.
            for i in stqdm(
                range(0, patches, self.batchsize),
                st_container=self.progress_bar,
                gui=False,
            ):
                X_batch = X_dataset[i : i + self.batchsize]
                X_batch = torch.from_numpy(X_batch).to(self.device)

                pred = self.model.predict_mask(X_batch)

                pred = pred.detach().cpu().numpy()
                pred = np.concatenate(pred, axis=2)
                mask.append(pred)

            mask = np.concatenate(mask, axis=2)

        return mask

    def _preprocess(self, X_spec):
        X_mag = np.abs(X_spec)
        X_phase = np.angle(X_spec)

        return X_mag, X_phase

    def _postprocess(self, mask, X_mag, X_phase):
        if self.postprocess:
            mask = merge_artifacts(mask)

        y_spec = mask * X_mag * np.exp(1.0j * X_phase)
        v_spec = (1 - mask) * X_mag * np.exp(1.0j * X_phase)

        return y_spec, v_spec

    def separate(self, X_spec):
        X_mag, X_phase = self._preprocess(X_spec)

        n_frame = X_mag.shape[2]
        pad_l, pad_r, roi_size = make_padding(n_frame, self.cropsize, self.offset)
        X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode="constant")
        X_mag_pad /= X_mag_pad.max()

        mask = self._separate(X_mag_pad, roi_size)
        mask = mask[:, :, :n_frame]

        y_spec, v_spec = self._postprocess(mask, X_mag, X_phase)

        return y_spec, v_spec


@st.cache_resource(show_spinner=False)
def load_model(pretrained_model, n_fft=2048):
    model = nets.CascadedNet(n_fft, 32, 128)
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        model.to(device)
    # elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
    #     device = torch.device("mps")
    #     model.to(device)
    else:
        device = torch.device("cpu")
    model.load_state_dict(torch.load(pretrained_model, map_location=device))
    return model, device


# @st.cache_data(show_spinner=False)
def separate(
    input,
    model,
    device,
    output_dir,
    batchsize=4,
    cropsize=256,
    postprocess=False,
    hop_length=1024,
    n_fft=2048,
    sr=44100,
    progress_bar=None,
    only_no_vocals=False,
):
    X, sr = librosa.load(input, sr=sr, mono=False, dtype=np.float32, res_type="kaiser_fast")
    basename = os.path.splitext(os.path.basename(input))[0]

    if X.ndim == 1:
        # mono to stereo
        X = np.asarray([X, X])

    X_spec = wave_to_spectrogram(X, hop_length, n_fft)

    with torch.no_grad():
        sp = Separator(model, device, batchsize, cropsize, postprocess, progress_bar=progress_bar)
        y_spec, v_spec = sp.separate(X_spec)

    base_dir = f"{output_dir}/vocal_remover/{basename}"
    os.makedirs(base_dir, exist_ok=True)

    wave = spectrogram_to_wave(y_spec, hop_length=hop_length)
    try:
        sf.write(f"{base_dir}/no_vocals.mp3", wave.T, sr)
    except Exception:
        logging.error("Failed to write no_vocals.mp3, trying pydub...")
        pydub_write(wave, f"{base_dir}/no_vocals.mp3", sr)
    if only_no_vocals:
        return
    wave = spectrogram_to_wave(v_spec, hop_length=hop_length)
    try:
        sf.write(f"{base_dir}/vocals.mp3", wave.T, sr)
    except Exception:
        logging.error("Failed to write vocals.mp3, trying pydub...")
        pydub_write(wave, f"{base_dir}/vocals.mp3", sr)


def pydub_write(wave, output_path, frame_rate, audio_format="mp3"):
    # Ensure the wave data is in the right format for pydub (mono and 16-bit depth)
    wave_16bit = (wave * 32767).astype(np.int16)

    audio_segment = AudioSegment(
        wave_16bit.tobytes(),
        frame_rate=frame_rate,
        sample_width=wave_16bit.dtype.itemsize,
        channels=1,
    )
    audio_segment.export(output_path, format=audio_format)
