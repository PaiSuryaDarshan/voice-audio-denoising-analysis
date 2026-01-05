"""
Library-based DSP implementation for video audio denoising.

A second implementation uses an existing noise reduction library 
to perform background noise suppression with significantly reduced 
code complexity.

This version is included for contrast and comparison only. 
It demonstrates how higher-level abstractions trade implementation 
control for speed of development and maintainability.
"""

import subprocess
from pathlib import Path

import soundfile as sf
import noisereduce as nr
import numpy as np
import os
import tempfile

def run(cmd: list[str]) -> None:
    """
    Execute a shell command and raise an error if it fails.
    Output is suppressed for cleaner logs.
    """
    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def denoise_video(
    input_video: str,
    output_video: str,
    sample_rate: int = 16000,
) -> None:
    """
    End-to-end video audio denoising pipeline.

    Steps:
    1) Extract audio from the input video
    2) Apply noise reduction to the audio signal
    3) Remux the cleaned audio back into the original video
    """

    # Create a temporary working directory for intermediate audio files
    with tempfile.TemporaryDirectory() as tmp:
        audio_in = os.path.join(tmp, "audio.wav")
        audio_out = os.path.join(tmp, "audio_clean.wav")

        # -------------------------------------------------
        # 1. Extract audio from video
        #    - Convert to mono
        #    - Resample to a speech-friendly rate
        # -------------------------------------------------
        run([
            "ffmpeg", "-y",
            "-i", input_video,
            "-ac", "1",
            "-ar", str(sample_rate),
            audio_in,
        ])

        # -------------------------------------------------
        # 2. Apply noise reduction to the extracted audio
        # -------------------------------------------------
        audio, sr = sf.read(audio_in)        # Load audio samples
        audio = audio.astype(np.float32)     # Ensure float format for processing

        clean_audio = nr.reduce_noise(
            y=audio,
            sr=sr,
            prop_decrease=0.9                # Strength of noise suppression
        )

        sf.write(audio_out, clean_audio, sr) # Save cleaned audio

        # -------------------------------------------------
        # 3. Remux cleaned audio back into the original video
        #    - Video stream is copied without re-encoding
        # -------------------------------------------------
        run([
            "ffmpeg", "-y",
            "-i", input_video,
            "-i", audio_out,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-shortest",
            output_video,
        ])


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    denoise_video(
        input_video=str(Path(__file__).resolve().parents[1] / "input" / "input.mp4"),
        output_video=str(Path(__file__).resolve().parents[1] / "output" / "output_standard_denoise.mp4"),
    )
