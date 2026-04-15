# 08.2 Radar Content Inspection

## Goal
Inspect sampled radar detections at the content level and visualize their spatial and attribute distributions.

## Why this stage matters
A radar topic can be structurally valid while still containing implausible or poor-quality detections.
This stage checks actual detection values and plots their distribution.

## Diagnostics performed
- sampled-frame XY scatter
- radial velocity distribution
- signal-to-noise ratio distribution
- radar cross section distribution
- point count distribution
- per-frame spatial bounds and validity ratio

## Command

```bash
python3 -m scripts.08_2_radar_content_inspection
```

## Output Saved
`outputs/tables/radar_content_sampled.csv`
`outputs/plots/radar_xy_sample_*.png`
`outputs/plots/radar_radial_velocity_hist.png`
`outputs/plots/radar_snr_hist.png`
`outputs/plots/radar_rcs_hist.png`
`outputs/plots/radar_point_count_hist.png`

## Interpretations

The plots are speaking:

### 1. Point-count histogram

**This looks healthy.**

**Interpretation:**

- sampled frames span a reasonable range of detection counts
- no collapse to near-zero detections
- no absurd explosion in count
- variability is present, which is normal for radar

So the radar is not producing a fixed dense grid. It is producing a variable set of detections, which is expected.

### 2. Radial velocity histogram

**This is very informative.**

**Interpretation:**

- strong concentration near low radial velocity values
- most detections are near stationary or slowly moving relative speed
- some spread exists, but not extreme

That is realistic in many outdoor/static-environment scenes where most returns are from stationary structures and only a smaller subset carries strong Doppler motion.

**One thing to note:** your first sampled frame has:

radial_velocity_mean ≈ -0.95  
radial_velocity_std  ≈ 8.66

while later sampled frames can be much tighter.  
So radar velocity content seems scene/frame dependent, which is normal.

### 3. RCS histogram

**This looks good.**

**Interpretation:**

- broad spread
- centered slightly below zero
- tails on both sides
- not collapsed or degenerate

That suggests radar cross section is being meaningfully populated and can be useful later to characterize target strength.

4. SNR histogram

This is also interesting.

Interpretation:

- values spread across a moderate range
- strong pile-up near the upper end

That upper-edge pile-up may indicate:

clipping/saturation at a driver threshold,
capped reporting,
or a common maximum-confidence style value.

This is not necessarily bad, but it is worth documenting.

So it can put as: SNR is populated and informative, though the upper-end concentration suggests possible clipping or thresholding behavior.

### 5. XY scatter

**This is the most important content plot.**

**Interpretation:**

- detections are sparse and clustered
- detections extend out to large forward distances
- left/right spread is plausible
- returns look object-like, not dense-surface-like

This is exactly radar behavior.

Compared to LiDAR:

LiDAR gave dense environmental surfaces  
radar gives sparse clusters and target-like detections

That means the radar is behaving in a physically believable way.

Also, your sample frame stats support this:

x_max around 149–152 m  
radial_distance_mean around 47–59  
valid_ratio = 1.0  

So the detections are:

all valid in sampled frames,  
far-reaching,  
body-frame centered,  
and spatially plausible.

## Initial findings

The sampled radar content inspection indicates that the radar detections are physically plausible and useful as a sparse supporting sensor.

### XY scatter inspection
The sampled XY plots show:
- sparse clustered detections rather than dense surface sampling
- plausible left/right spread
- forward detections extending to large distances
- object-like target groupings rather than LiDAR-style continuous geometry

This is consistent with expected radar behavior.

### Point-count distribution
The point-count histogram shows a variable number of detections per sampled frame.
This is normal for radar, since the number of detections depends on scene structure, clutter filtering, and target visibility.

### Radial velocity distribution
The radial velocity distribution is strongly concentrated near lower relative velocities, with some spread.
This suggests that many detections correspond to stationary or slowly moving objects, which is plausible for an outdoor environment.

### Radar cross section (RCS)
The RCS distribution shows a broad spread and appears meaningfully populated.
This indicates that target strength information is available and may be useful for later characterization of detections.

### Signal-to-noise ratio (SNR)
The SNR distribution is populated and informative.
A visible concentration near the upper end suggests possible clipping, thresholding, or capped reporting behavior in the radar driver.

## Working conclusion

The radar topic is now confirmed as:
- structurally consistent
- content-valid
- physically plausible
- useful as a sparse supporting perception sensor

It should not be treated like LiDAR, but it is suitable for later cross-sensor analysis and detection-level inspection.

## Scope note

This stage used sampled radar frames for lightweight inspection.
The results support the conclusion that the radar stream is healthy, but they do not yet replace full-sequence detection-level analysis.

So, Basically in this dataset, 

GNSS   → rejected
IMUs   → usable, two strong candidates
LiDAR  → strongest main geometric sensor
Radar  → healthy sparse supporting sensor

These are updates until here.

