# 09.1 Camera Timing and Stereo Consistency

## Goal
Evaluate image timing behavior and check whether left and right camera streams are close enough in time for stereo-style use.

## Inputs
- `outputs/tables/camera_image_metadata.csv`
- `outputs/tables/camera_info_metadata.csv`

## Diagnostics performed
- left image dt statistics
- right image dt statistics
- left camera_info dt statistics
- right camera_info dt statistics
- nearest left-right pairing time difference
- simple stereo pairing quality thresholds

## Command

```bash
python3 -m scripts.09_1_camera_timing
```

# Output Saved
`outputs/tables/camera_timing_summary.txt`
`outputs/tables/camera_stereo_pairing.csv`

# Interpretations - Final conclusion

The stereo camera timing is good enough for stereo-style use in most of the recording.

### Left/right timing
The left and right compressed image streams have very similar timing behavior:
- nearly identical mean dt
- identical median dt
- similar burst/pause structure

### Stereo pairing quality
Nearest left-right pairing shows strong synchronization:
- mean absolute time difference is very small
- median difference is zero
- most image pairs fall within 5 ms

This indicates that the stereo pair is well aligned in time for most of the sequence.

### Camera info behavior
The camera_info topics are frequent and appear to include repeated timestamps or closely repeated messages.
These should be treated primarily as calibration/support metadata rather than the main timing reference.

## Working decision

The stereo camera block is now confirmed as:
- structurally healthy
- timing-usable
- suitable for sampled visual content inspection
- potentially suitable for later stereo-oriented analysis, subject to image quality

** GOTO docs/09_2_camera_content/README.md to know more in depth into the content of camera.