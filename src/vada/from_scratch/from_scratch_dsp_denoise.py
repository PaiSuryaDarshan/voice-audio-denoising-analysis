"""
From-scratch DSP implementation for video audio denoising.

This file intentionally contains the full signal processing pipeline
in a single, linear script for learning and inspection purposes.

The implementation prioritises transparency and step-by-step clarity
over modularity or reuse. The below code was NOT intended for use 
as a production library.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import wave


# ============================================================
# FFmpeg runner
# ============================================================

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def find_ffmpeg() -> str:
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise FileNotFoundError(
            "ffmpeg not found on PATH. Install it (e.g. `brew install ffmpeg`) "
            "or add it to your PATH."
        )
    return ffmpeg


# ============================================================
# WAV I/O (PCM16 mono/stereo -> mono)
# ============================================================

def wav_read_pcm16(path: str):
    with wave.open(path, "rb") as wf:
        nch = wf.getnchannels()
        sw = wf.getsampwidth()
        sr = wf.getframerate()
        n = wf.getnframes()
        if sw != 2:
            raise ValueError("Only PCM16 WAV supported (16-bit).")
        raw = wf.readframes(n)

    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0

    if nch == 2:
        x = x.reshape(-1, 2).mean(axis=1)
    elif nch != 1:
        raise ValueError("Only mono/stereo supported.")
    return x, sr


def wav_write_pcm16(path: str, x: np.ndarray, sr: int):
    x = np.clip(x, -1.0, 1.0)
    y = (x * 32767.0).astype(np.int16)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(y.tobytes())


# ============================================================
# Simple biquad high-pass
# ============================================================

def biquad_highpass(x: np.ndarray, sr: int, fc: float = 80.0, q: float = 0.707):
    w0 = 2.0 * np.pi * fc / sr
    cosw0 = np.cos(w0)
    sinw0 = np.sin(w0)
    alpha = sinw0 / (2.0 * q)

    b0 = (1 + cosw0) / 2
    b1 = -(1 + cosw0)
    b2 = (1 + cosw0) / 2
    a0 = 1 + alpha
    a1 = -2 * cosw0
    a2 = 1 - alpha

    b0 /= a0; b1 /= a0; b2 /= a0
    a1 /= a0; a2 /= a0

    y = np.zeros_like(x, dtype=np.float32)
    x1 = x2 = 0.0
    y1 = y2 = 0.0
    for i in range(len(x)):
        xn = float(x[i])
        yn = b0 * xn + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        y[i] = yn
        x2, x1 = x1, xn
        y2, y1 = y1, yn
    return y


# ============================================================
# STFT / ISTFT (Hann, overlap-add)
# ============================================================

def stft(x: np.ndarray, n_fft: int, hop: int):
    win = np.hanning(n_fft).astype(np.float32)
    if len(x) < n_fft:
        x = np.pad(x, (0, n_fft - len(x)), mode="constant")
    n_frames = 1 + (len(x) - n_fft) // hop
    frames = np.stack([x[i * hop : i * hop + n_fft] * win for i in range(n_frames)], axis=0)
    X = np.fft.rfft(frames, n=n_fft, axis=1)
    return X, win, len(x)


def istft(X: np.ndarray, win: np.ndarray, hop: int, out_len: int):
    n_frames, n_bins = X.shape
    n_fft = (n_bins - 1) * 2
    y_len = n_fft + (n_frames - 1) * hop
    y = np.zeros(y_len, dtype=np.float32)
    wsum = np.zeros(y_len, dtype=np.float32)

    frames = np.fft.irfft(X, n=n_fft, axis=1).astype(np.float32)
    for i in range(n_frames):
        start = i * hop
        y[start:start+n_fft] += frames[i] * win
        wsum[start:start+n_fft] += win * win

    y = y / np.maximum(wsum, 1e-10)
    return y[:out_len]


# ============================================================
# Improved DSP denoiser (adaptive noise tracking)
# ============================================================

def denoise_dsp(
    x: np.ndarray,
    sr: int,
    n_fft: int = 1024,
    hop: int = 256,
    init_noise_seconds: float = 0.6,
    noise_update: float = 0.985,
    dd_alpha: float = 0.98,
    gain_smooth: float = 0.85,
    oversub: float = 1.2,
    floor_base: float = 0.06,
    hp_fc: float | None = 80.0,
):
    if hp_fc is not None and hp_fc > 0:
        x = biquad_highpass(x, sr, fc=hp_fc)

    X, win, out_len = stft(x, n_fft=n_fft, hop=hop)
    mag = np.abs(X).astype(np.float32)
    phase = np.angle(X).astype(np.float32)
    P = mag * mag

    n_frames, n_bins = P.shape
    freqs = np.linspace(0.0, sr / 2.0, n_bins, dtype=np.float32)

    init_frames = int(max(1, (init_noise_seconds * sr - n_fft) // hop))
    init_frames = min(init_frames, n_frames)
    Npsd = np.median(P[:init_frames, :], axis=0).astype(np.float32) + 1e-12

    f_norm = freqs / (sr / 2.0 + 1e-12)
    floor_shape = (0.7 + 0.6 * np.sqrt(f_norm)).astype(np.float32)

    prev_G = np.ones(n_bins, dtype=np.float32)
    prev_post_snr = np.ones(n_bins, dtype=np.float32)
    prev_gain = np.ones(n_bins, dtype=np.float32)

    Y = np.zeros_like(X)

    for t in range(n_frames):
        Pt = P[t]
        gamma = np.maximum(Pt / Npsd, 1e-6)

        xi = dd_alpha * (prev_G * prev_G) * prev_post_snr + (1.0 - dd_alpha) * np.maximum(gamma - 1.0, 0.0)
        xi = np.maximum(xi, 1e-6)

        G = xi / (xi + 1.0)
        G = np.clip(G ** oversub, 0.0, 1.0)
        G = gain_smooth * prev_gain + (1.0 - gain_smooth) * G

        floor = np.clip(floor_base * floor_shape, 0.02, 0.25).astype(np.float32)
        G = np.maximum(G, floor)

        speech_prob = np.clip((gamma - 1.0) / 5.0, 0.0, 1.0)
        beta = noise_update + (1.0 - noise_update) * speech_prob
        Npsd = np.maximum(beta * Npsd + (1.0 - beta) * Pt, 1e-12)

        Ymag = (np.sqrt(Pt) * G).astype(np.float32)
        Y[t] = Ymag * (np.cos(phase[t]) + 1j * np.sin(phase[t]))

        prev_G = G
        prev_post_snr = gamma
        prev_gain = G

    return istft(Y, win, hop=hop, out_len=out_len)


# ============================================================
# Video wrapper: mp4 -> wav -> DSP -> mp4
# (Only requires: input file + output directory path)
# Output filename is fixed: output_manual_dsp_denoise.mp4
# ============================================================

def denoise_video_mp4(
    input_mp4: str | Path,
    output_dir: str | Path,
    sample_rate: int = 16000,
):
    input_mp4 = Path(input_mp4)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_mp4 = output_dir / "output_manual_dsp_denoise.mp4"
    ffmpeg = find_ffmpeg()

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        audio_wav = tmp / "audio.wav"
        audio_clean = tmp / "audio_clean.wav"

        # 1) Extract PCM16 WAV from input video
        run([
            ffmpeg, "-y",
            "-i", str(input_mp4),
            "-vn",
            "-ac", "1",
            "-ar", str(sample_rate),
            "-c:a", "pcm_s16le",
            str(audio_wav),
        ])

        # 2) Denoise WAV with from-scratch DSP
        x, sr = wav_read_pcm16(str(audio_wav))
        y = denoise_dsp(x, sr)
        wav_write_pcm16(str(audio_clean), y, sr)

        # 3) Remux cleaned audio back into video (copy video stream)
        run([
            ffmpeg, "-y",
            "-i", str(input_mp4),
            "-i", str(audio_clean),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_mp4),
        ])

    return output_mp4


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python from_scratch_dsp_denoise.py <input.mp4> <output_dir/>")
        sys.exit(1)

    out_path = denoise_video_mp4(sys.argv[1], sys.argv[2])
    print(f"Done: {out_path}")
