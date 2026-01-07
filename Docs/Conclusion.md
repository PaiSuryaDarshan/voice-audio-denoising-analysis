# Conclusion

This project set out to compare two audio denoising approaches — a manually implemented digital signal processing (DSP) pipeline and a standard library-based denoising method — against the original noisy input, using **quantitative signal analysis**.

From an initial human listening perspective, both denoising methods improved perceptual clarity relative to the raw input. However, the comparison between the two revealed a clear trade-off: the **manual DSP output** retained more loudness and presence, but introduced an audible artefact in the form of unnatural pitch modulation (“pitch wobble”), whereas the **standard denoising method** produced a quieter but perceptually cleaner and more stable output.

This subjective impression was subsequently examined and validated through a series of signal-level analyses. Peak-to-peak and RMS measurements showed progressively stronger amplitude suppression from input → manual DSP → standard denoising. While this confirmed effective noise attenuation, it also explained the reduced loudness of the standard method. Signal-to-noise ratio (SNR) analysis further demonstrated that aggressive gain reduction can lower numerical SNR despite improving perceptual clarity, highlighting a known limitation of raw SNR as a sole quality metric.

Crucially, the pitch wobble artefact observed in the manual DSP output was not merely anecdotal. A focused analysis of frame-to-frame fundamental frequency behaviour in voiced regions revealed substantially increased pitch dispersion, a broader ΔF₀ distribution, and a higher octave flip rate relative to both the input and the standard denoising method. These quantitative pitch metrics provide strong statistical evidence that the manual DSP pipeline introduced instability into the pitch trajectory, directly explaining the perceived modulation artefact.

Overall, this work demonstrates that while custom DSP approaches can offer intuitive control and competitive noise reduction, they are also more susceptible to unintended artefacts if temporal and spectral interactions are not carefully managed. In contrast, standard denoising pipelines appear to prioritise pitch stability and perceptual cleanliness, albeit at the cost of reduced loudness.

---

## Limitations and Future Work

This analysis was conducted using a single speech recording, with a fixed speaker pitch range and a specific noise profile. As a result, the conclusions drawn here should be interpreted as **case-specific rather than universal**.

Out of my own curioisty, an extension of this work I would like to do at some point would be to repeat the analysis across:

- Multiple speakers with different fundamental pitch ranges (e.g. lower and higher voices),
- Varying noise amplitudes and noise types (stationary vs. non-stationary),
- Different recording conditions and devices.
