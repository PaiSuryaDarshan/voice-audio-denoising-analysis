# Results and discussions

## 0. Human Opinion

<h3>What do I think of the results, the first time I heard it ?</h3>

A special thanks to my friend Abby, 3rd year undergrad math student at UCL, who is quoted verbatim below.

```quote
When I first listened to the outputs, I wasn’t trying to analyse anything — I was just listento it.

Inoticed how both denoising approaches compared to the original input and also how they compared to each other.

However, I found myself paying attention to something that kinda bothered me, some weird voice modulation stuff. An unnatural eerie deepening movement / fluctuation on the manual sample I think.
```

With those impressions in mind — and knowing what to listen for — the next step was to stop relying purely on perception and actually look at the signal.

So let's "SEE" what that sounded like...

## 1.Finding the First Active Sample (FAS)

![as](../Images/first_active_sample_fail.png)

### Reasoning

There seems to be no activity within the frst few 50 seconds of the audio. This expected because Mobile phones often introduce a short audio dead zone (lasting between 50-250ms usually (in my experince atleast)) at the beginning because <b>microphone and codec initialisation</b> occurs only after the video capture starts and this audio dead zone also allows for other orthogonal systems like Automatic Gain Control (AGC) and noise suppression to stabilise. Additionally, Some devices intentionally pad the start with silence to avoid clicks or transients.

To avoid manual heuristics and iterative trial-and-error tuning, a systematic threshold scan was implemented to identify the first region exhibiting signal activity which resulted in a plot similar to one expected. (Shown below)

![as](../Images/first_active_sample.png)

Using the (absolute) amplitude thresholding method (with
a threshold of $1 \times 10^{-3}$.), The first active sample signal was recorded at 173 ms into the recoding.

## 2.Peak to Peak (on FAS)

![as](../Images/p2p.png)

### Interpretation

The peak-to-peak (P2P) plots compare the intial instantaneous dynamic range of the signal over the same short-time window (173-223 ms). The input signal exhibits the largest peak-to-peak excursions, reflecting both speech content and significant background noise. The manual DSP output shows a noticeable reduction in peak-to-peak range, indicating effective attenuation of large-amplitude noise components, but still retains moderate variability due to preserved transient speech peaks. In contrast, the standard denoising output displays the smallest peak-to-peak range, suggesting stronger overall amplitude suppression and tighter dynamic control. This indicates more aggressive noise reduction, but also raises the possibility of partial signal over-attenuation.

## 3.Root Mean Square Amplitude (of FAS)

![as](../Images/RMS_50ms.png)

The Root Mean Square (RMS) amplitude of a discrete-time signal is defined as:

$$
\mathrm{RMS}(x) = \sqrt{\frac{1}{N} \sum_{n=1}^{N} x_n^2}
$$

**where:**

- $x_n$ is the $n$-th sample of the signal,
- $N$ is the total number of samples in the analysed window,
- squaring ensures positive and negative excursions contribute equally,
- averaging emphasises sustained signal energy rather than isolated peaks.

### Interpretation

RMS amplitude therefore provides an **energy-based measure of signal strength**, making it more robust and perceptually relevant than peak-based metrics when evaluating denoising performance.

The RMS plots capture the energy content of the signal rather than isolated extrema. The input signal shows consistently higher RMS levels, consistent with sustained background noise contributing to overall energy. The manual DSP signal exhibits a reduced RMS level while still preserving noticeable temporal energy fluctuations corresponding to speech activity. The standard denoising output has the lowest RMS amplitude and appears nearly flat across the window, indicating substantial suppression of both noise and low-level signal components. While this confirms strong noise reduction, it also explains the perceptual impression of reduced loudness and potential loss of speech presence.

## 4.Signal Noise Ratio (SNR)

(A) Waveform overlay
![as](../Images/snr_wf.png)

(B) SNR comparison
![as](../Images/snr_lvl.png)

The Signal-to-Noise Ratio (SNR) is defined as:

$$
\mathrm{SNR}_{\mathrm{dB}} = 10 \log_{10}\!\left(\frac{P_{\text{signal}}}{P_{\text{noise}}}\right)
$$

**where:**

- $P_{\text{signal}}$ is the average signal power,
- $P_{\text{noise}}$ is the average noise power,
- the logarithmic scale expresses the ratio in decibels (dB).

In this analysis, signal and noise regions are estimated using a robust, MAD-based amplitude threshold, and powers are computed over their respective regions.

### Interpretation

**(A) Waveform overlay and per-track scaling**

From Plot A, the _Standard_ denoising output operates at a much lower absolute amplitude scale (note the tighter y-axis range) compared to both the Input and Manual DSP outputs. This aggressive attenuation suppresses not only background noise but also a significant portion of the speech energy. The overlay subplot (top of Plot A) shows that, despite this reduced scale, the Standard method preserves a clean and temporally stable speech structure, which explains why it subjectively sounds the clearest, albeit very quiet.

In contrast, the Manual DSP output retains a higher overall amplitude, making it louder, but with more residual modulation and artefacts visible in the waveform.

**(B) SNR comparison**

In Plot B, the Standard method exhibits the _lowest SNR_ despite sounding the cleanest. This is not contradictory: because SNR is computed as a _relative power ratio_, the heavy attenuation (also shown on plot A, pay attention to the y-axis values) applied by the Standard method reduces the estimated signal power more than the noise power under the chosen segmentation threshold. As a result, the numerical SNR decreases even though perceptual clarity improves.

In short:

- **Standard denoising** → strongest attenuation → lowest absolute signal level → lower measured SNR, but highest perceptual clarity.
- **Manual DSP** → moderate attenuation → higher loudness → intermediate SNR, with audible artefacts.
- **Input** → highest signal power → highest SNR numerically, but poorest perceptual quality due to strong noise presence.

This highlights a key limitation of raw SNR: it does not always align with perceived audio quality when strong gain reduction is involved.

## 5.Relative Loudness

![as](../Images/relative_loudness_levels.png)

The mean signal level is computed in decibels relative to full scale (dBFS) using the RMS amplitude:

$$
\mathrm{Level}_{\mathrm{dBFS}} = 20 \log_{10}\!\left(\mathrm{RMS}\right)
$$

with

$$
\mathrm{RMS} = \sqrt{\frac{1}{N}\sum_{n=1}^{N} x[n]^2}
$$

**where:**

- $x[n]$ is the discrete-time audio signal,
- $N$ is the total number of samples,
- dBFS is referenced to a full-scale signal of amplitude 1.0, hence values are typically negative for real recordings.

### Interpretation

This plot visualises the **relative loudness** of the three signals on a common dBFS scale. The Input signal has the highest mean level, indicating it is the loudest overall. The Manual DSP output is noticeably quieter, reflecting moderate attenuation introduced during denoising. The Standard method has the lowest mean level, confirming that it applies the strongest gain reduction.

This explains the audible impression: the Standard output sounds the quietest, while the Manual DSP is louder.

This plot (further complemented with the plot 5A) therefore captures the trade-off between **perceived clarity** and **absolute loudness**, rather than indicating signal quality on its own.

## 6. [Personal favourite] Pitch Step Size Distribution: Explaining the pitch wobble

![as](../Images/distribution_of_pitch_step_sizes.png)

What Abby was talking about when she said (in verbatim), "weird voice modulation stuff. An unnatural eerie deepening movement / fluctuation on the manual sample I think.", she was reffering to "The Pitch Wobble" atefact.

This analysis evaluates **pitch stability** across the input signal, the manual DSP denoising pipeline, and the standard denoising method by examining **frame-to-frame fundamental frequency (F₀) behaviour** in voiced regions only.

### Firstly, What the Histogram Shows (ΔF₀ Distribution)

The histogram plots the distribution of **pitch step sizes**

$$
\Delta F_0(t) = F_0(t+1) - F_0(t)
$$

between consecutive voiced frames.

- A **narrow distribution** concentrated around 0 Hz indicates **stable pitch tracking**.
- A **wider distribution with long tails** indicates **pitch wobble / jitter**, often perceived as instability or artificial modulation.

Visually:

- **Manual DSP** exhibits a noticeably **broader ΔF₀ distribution**, with more large jumps.
- **Standard denoising** shows fewer extreme excursions.
- **Input** is the most tightly clustered overall.

### Quantitative Pitch Metrics (Voiced Frames Only)

<div align="center">

| Metric               |      Input | Manual DSP | Standard Denoising |
| -------------------- | ---------: | ---------: | -----------------: |
| Mean F₀ (Hz)         | **148.63** | **177.56** |         **159.62** |
| Std(F₀) (Hz)         |      39.19 |      58.34 |              56.84 |
| IQR(F₀) (Hz)         |  **20.75** | **109.77** |          **22.94** |
| RMS(ΔF₀) (Hz)        |      37.77 |  **48.78** |          **52.78** |
| Median(ΔF₀) (Hz)     |       1.41 |       1.35 |               1.41 |
| Octave flip rate (%) |       7.41 |   **9.88** |               9.13 |

</div>

- The **Manual DSP** pipeline exhibits **severely increased pitch dispersion** (very large IQR) and a higher octave flip rate, quantitatively explaining the observed **pitch wobble artefacts**.
- The **Standard** method maintains a **controlled pitch spread** comparable to the input, despite slightly elevated frame-to-frame fluctuations.
- The **Input** shows expected, moderate natural pitch variability with relatively low dispersion.

### Interpretation

- **Manual DSP introduces significant pitch instability**, evidenced by:
  - Much larger IQR(F₀)
  - Broader ΔF₀ distribution
  - Higher octave flip rate
- **Standard denoising preserves pitch structure more consistently**, despite aggressive noise reduction.
- The **input signal provides the reference baseline**, with natural but bounded pitch variation.

**Conclusion:**  
The pitch wobble artefact observed in the manual DSP output is **statistically validated** by increased pitch dispersion and jitter metrics, rather than being a purely subjective listening effect.

The concept of a pitch wobble was completeky new to me, and showing it visually and statistically was more so difficult. Yet, none the less perseverence did not fail.

## Summary

see [conclusion.md](Conclusion.md)

## Note to reader who got this far,

Further Analysis not covered in this document that can be found in the comparative signal analysis notebook linked [HERE](../notebooks/statistical_comparison_and_signal_analysis.ipynb).
