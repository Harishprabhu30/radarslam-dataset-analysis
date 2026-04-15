# 09.2 Camera Sampled Image Inspection

## Goal
Inspect sampled stereo image pairs visually and compute lightweight image-quality indicators.

## Why this stage matters
A camera stream may be structurally and temporally valid while still being difficult to use because of:
- poor lighting
- blur
- weak texture
- heavy compression
- poor stereo visual consistency

## Inputs
- stereo pairing table from Stage 9.1
- compressed image topics from the bag

## Diagnostics performed
- sampled left/right image decoding
- side-by-side stereo pair export
- image brightness mean
- image brightness standard deviation

## Command

```bash
python3 -m scripts.09_2_camera_content_inspection
```

## Outputs Saved
`outputs/tables/camera_content_sampled.csv`
`outputs/plots/camera_samples/*.png`

# Interpretations - 

## 1. Camera orientation observation

Sampled stereo images appear upside down in both left and right channels.

This suggests that:
- the stereo camera was likely mounted inverted, or
- the acquisition pipeline did not apply orientation correction.

Because both left and right images are rotated consistently, this does not by itself invalidate stereo usability.
It should be treated as a camera orientation issue rather than image corruption.


### 2. Stereo consistency

**Left/right stereo consistency looks good**

The sampled stereo pairs visually match well, and most sampled pairs have:

abs_time_diff_s = 0.0

So the stereo pair is not only structurally and temporally healthy, but also visually consistent.

### 3. Resolution

**Resolution is stable**

All sampled frames are:

1024 × 576

So the image dimensions are stable.

### 4. Brightness/contrast

**Brightness/contrast look reasonable**

The brightness means and standard deviations are in plausible ranges and left/right values are close to each other.

That suggests:

- no obvious one-sided exposure failure
- no major left/right brightness mismatch
- enough contrast for scene interpretation

## Final conclusion

The sampled stereo image inspection indicates that the camera stream is visually usable.

### Visual content
The decoded stereo images show plausible outdoor scene content and do not exhibit obvious corruption.

### Stereo consistency
The sampled left/right pairs are visually consistent, and most sampled pairs have negligible time difference.
This supports the conclusion that the stereo pair is usable in both timing and visual correspondence.

### Image quality
The sampled image statistics show:
- stable resolution
- plausible brightness values
- similar left/right brightness behavior
- adequate contrast for visual scene interpretation

### Orientation observation
Both left and right images appear upside down.
This suggests that the stereo camera was likely mounted inverted, or that the acquisition pipeline did not apply an orientation correction.

Because both channels are rotated consistently, this should be treated as a camera orientation issue rather than image corruption.

## Working decision

The stereo camera block is now confirmed as:
- structurally healthy
- timing-usable
- visually usable
- potentially suitable as a supporting stereo/visual sensor, provided the orientation issue is handled appropriately in later use

## Scope note

This stage used sampled stereo pairs for lightweight visual inspection.
The results support camera usability, but they do not yet constitute a full visual odometry or stereo reconstruction evaluation.

** GOTO docs/10_final_robot_understanding/README to understand this robot and its story.
