# Video Audio Denoising (Digital Signal Processing Project)

<p align="center">
  <img src="IMAGES/0_SNR_FACE.png" alt="Waveform overlay (Input vs Manual DSP vs Standard)" width="800">
</p>

This repository documents a learning-focused digital signal processing (DSP) project centred on background noise suppression in the audio track of video recordings.

The project implements and analyses two parallel denoising approaches:

1.  a from-scratch DSP pipeline, explicitly implementing classical signal-processing components, and
2.  a baseline pipeline using an existing noise-reduction library for comparison.

The primary goal is to understand the behaviour, trade-offs, and limitations of manual DSP design relative to higher-level abstractions, using transparent, signal-level evaluation rather than black-box or perceptual-only assessment.

This repository is not intended as a production package.

## What the project currently does

The project implements an end-to-end audio denoising workflow using classical DSP techniques.

• Implements an audio denoising pipeline based on time–frequency analysis, including a fully from-scratch DSP implementation and a standard library-based baseline for comparison.

• Processes real-world audio extracted from video recordings, handling container conversion (MP4 → WAV → MP4) to enable reproducible signal-level analysis on realistic inputs.

• Automatically detects the first active audio region using a threshold-based scan, avoiding manual heuristics or trial-and-error selection of analysis windows.

• Applies energy-based noise suppression and signal conditioning techniques to reduce background noise while preserving primary signal structure.

• Evaluates denoising behaviour using signal-processing metrics, including:  
– RMS amplitude (global signal energy)  
– Short-time RMS analysis (frame-level energy variation)  
– Peak amplitude and peak-to-peak measures  
– Crest factor and peak-to-RMS ratio (dynamic range characterisation)  
– Relative percentage change with respect to the original signal

• Produces time-domain waveform comparisons across the original signal, the from-scratch DSP output, and the library-based output, using consistent scaling for fair visual interpretation.

• Generates time–frequency visualisations (spectrograms) to qualitatively assess noise suppression, harmonic structure preservation, and residual artefacts.

• Supports transparent comparison between denoising approaches, enabling inspection of trade-offs between noise reduction strength and signal preservation.

• Emphasises reproducibility, signal-level reasoning, and interpretable evaluation over opaque optimisation or perceptual scoring.

## What this project explicitly does not claim

The scope of this project is intentionally constrained.

• Does not implement machine learning, neural networks, or data-driven optimisation  
• Does not report perceptual quality metrics (e.g. PESQ, STOI)  
• Does not perform statistical hypothesis testing or formal benchmarking  
• Does not claim real-time operation or production deployment  
• Does not claim superiority of one approach over another

All observations are descriptive and exploratory.

## Project structure

The repository is organised to reflect the learning and comparison-driven nature of the work.

```text
video-audio-denoising/
├── from_scratch/
|   ├── DSP_Denoising_From_Scratch.pdf
│   └── from_scratch_dsp_denoise.py
│
├── library_dsp/
|   ├── Notes.md
│   └── library_denoise.py
│
├── notebooks/
|   ├── Results_and_discussion.md
│   └── signal_analysis_comparison.ipynb
│
├── examples/
│   ├── input/
│   │   └── input.mp4
│   └── output/
│       ├── output_from_scratch_dsp_denoise.mp4
│       └── output_standard_denoise.mp4
│
├── requirements.txt
├── README.md
└── .gitignore
```

• `from_scratch/` contains the from-scratch DSP implementation, kept as a single, linear script to preserve transparency of the full signal path.

• `library_dsp/` contains the baseline implementation using an existing noise-reduction library for contrast.

• `notebooks/` contains exploratory analysis notebooks used for waveform inspection, spectrogram analysis, and metric comparison. These notebooks are not part of the execution pipeline.

• `examples/` contains synthetic or non-sensitive example inputs and outputs for reproducibility and inspection.

## Benchmark verdict

The standard library-based noise reduction approach is used as a reference baseline against which the from-scratch DSP implementation is evaluated. Comparative analysis focuses on signal-level behaviour and measurable characteristics rather than perceptual or production-oriented claims.

This benchmarking process is currently ongoing, and the results presented here should be considered preliminary.

## Project Inspiration (A Short story)

I am no stranger to digital signal processing, especially having worked closely with highly sensitive spectroscopic machines andtuning in the lab. However, I never got the chance to use it on something real. Not a toy example or a clean dataset — just a real situation.

One evening early Dec 2025, while walking to grab a coffee, I recorded a short video because the moment felt nice and I wanted to share it with a few friends. When I watched it back later, the audio was… bad. Everything I said was muffled, the background noise was overwhelming, and turning the volume up just made it painful to listen to.

Normally, I would have dropped the file into an online denoiser and moved on. Instead, I thought: this is probably the cleanest excuse I’ll get to actually put myself to the test. I am never one to back away from a challenge, so I thought let me give it a shot.

I genuinely thought this would take an afternoon.

It didn’t.

What started as “let me remove some background noise” quickly turned into a much deeper problem involving time–frequency representations, stability issues, artefacts, and lots of trial, error, and reading. The project ended up stretching over nearly a month, growing far beyond the original idea.

But i stayed resilient and by the end of it, the real win wasn’t just cleaner audio — it was how much more clearly I understood the full DSP pipeline, its limitations, and why seemingly simple problems are rarely simple once you try to solve them properly.
