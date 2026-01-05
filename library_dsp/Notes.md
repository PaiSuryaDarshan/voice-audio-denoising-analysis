# Library-Based Audio Denoising — Conceptual Overview

This directory contains a baseline audio denoising implementation that relies on existing libraries rather than an explicit from-scratch DSP pipeline.

The purpose of this implementation is **comparative and educational**. It serves as a reference point against which the behaviour, transparency, and trade-offs of the from-scratch DSP approach can be examined.

This document explains, at a conceptual level, how the library-based process operates and how it differs from the explicit DSP pipeline implemented elsewhere in this repository.

# High-Level Processing Flow

The library-based denoising pipeline follows the same end-to-end structure as the from-scratch implementation, but abstracts away most signal-processing internals.

At a high level, the process consists of:

1.  **Audio extraction from video**  
    The audio track is extracted from the input video file, converted to a mono waveform, and resampled to a fixed sampling rate suitable for speech and general audio analysis.
2.  **Noise reduction using a pre-packaged algorithm**  
    The extracted waveform is passed to a noise-reduction function provided by an external library. This function internally performs time–frequency analysis, noise estimation, and spectral attenuation using predefined heuristics and parameters.
3.  **Audio remuxing**  
    The denoised audio is written back to disk and remultiplexed into the original video container, preserving the original video stream.

The overall data flow mirrors the from-scratch pipeline, but the internal signal-processing steps are encapsulated within the library.

# Role of External Libraries

The library-based implementation relies on two primary external components:

- **SoundFile (`soundfile`)** for audio input/output
- **NoiseReduce (`noisereduce`)** for noise suppression

Each plays a distinct role in the signal-processing chain.

# SoundFile: Audio I/O Layer

`SoundFile` is a Python interface to the `libsndfile` C library and is used exclusively for **reliable audio decoding and encoding**.

Within this project, `SoundFile` performs the following functions:

- decodes the extracted WAV file into a NumPy array representing the time-domain audio signal,
- handles sample format conversion (e.g. integer PCM to floating-point),
- preserves sampling rate and channel structure,
- writes the denoised signal back to disk in WAV format for remuxing.

`SoundFile` does **not** perform any denoising, filtering, or analysis.  
It simply provides a robust bridge between audio files and numerical arrays.

# NoiseReduce: Core Denoising Logic

The `noisereduce` library encapsulates a **spectral noise reduction algorithm** operating in the time–frequency domain.

At a conceptual level, a call of the form:

```python
nr.reduce_noise(y=audio, sr=sr, ...)
```

performs the following steps internally.

### 1\. Time–Frequency Transformation

The input time-domain signal is segmented into overlapping frames and transformed into the frequency domain, typically using a Short-Time Fourier Transform (STFT).

This produces a complex-valued time–frequency representation where:

- each frame corresponds to a short time window,
- each frequency bin represents energy at a specific frequency.

This step is analogous to the explicit STFT implemented in the from-scratch pipeline, although the precise parameters (window type, overlap, FFT size) are chosen internally by the library.

### 2\. Noise Profile Estimation

The algorithm estimates the spectral characteristics of background noise.

Depending on configuration and signal length, this is typically achieved by:

- analysing low-energy regions of the signal, or
- inferring noise statistics from the overall signal distribution.

The strategy used to identify noise-dominated frames is **not exposed** to the user and is handled internally by the library.

The result is an estimated noise spectrum or noise power profile across frequency bins.

### 3\. Spectral Attenuation (Noise Suppression)

For each time–frequency bin, the algorithm computes a **gain factor** based on the estimated noise level.

Conceptually:

- frequency components dominated by noise are attenuated,
- components likely dominated by signal are preserved.

The `prop_decrease` parameter controls the **strength of suppression**, scaling how aggressively noise-dominated bins are reduced.

This stage is conceptually related to classical spectral subtraction or Wiener-style filtering, implemented using library-specific heuristics.

### 4\. Signal Reconstruction

After attenuation, the modified spectral representation is transformed back into the time domain using an inverse STFT.

Overlap–add reconstruction is applied to reassemble the continuous waveform from individual frames.

The result is a time-domain signal with reduced background noise.

# Key Characteristics of the Library-Based Approach

The library-based denoising process has several defining properties:

- **Algorithmic abstraction**  
  Core DSP steps (STFT parameters, noise estimation logic, gain computation) are hidden from the user.
- **Heuristic-driven behaviour**  
  Noise suppression relies on built-in heuristics rather than explicitly defined, user-controlled models.
- **Limited inspectability**  
  Intermediate quantities such as noise power spectra, frame-level gains, or SNR estimates are not directly accessible.
- **Parameter-level control only**  
  Behaviour is influenced via high-level parameters rather than explicit algorithmic structure.

# Relationship to the From-Scratch Implementation

This implementation should be read alongside the accompanying documentation for the from-scratch DSP pipeline.

Where the from-scratch approach prioritises:

- explicit algorithmic structure,
- inspectable intermediate quantities,
- step-by-step signal reasoning,

the library-based approach prioritises:

- abstraction,
- brevity,
- ease of use.

The comparison between the two is the primary learning objective of this project.

# Scope and Limitations

This implementation:

- is not intended as a production-ready solution,
- does not expose internal model parameters or guarantees,
- does not provide perceptual quality assessment,
- is used solely for exploratory and comparative analysis.

# Scope Clarification

This document describes the **conceptual DSP workflow** implemented by the library based on documented behaviour and standard spectral denoising practices.

No claims are made regarding:

- exact internal implementation details,
- perceptual optimality,
- equivalence to the from-scratch pipeline.
