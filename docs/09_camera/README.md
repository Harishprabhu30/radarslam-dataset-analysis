# 09 Camera Structural Inspection

## Goal
Inspect the stereo camera topics structurally before timing and image-content analysis.

## Topics analysed
- /zed2i/zed_node/left/image_rect_color/compressed
- /zed2i/zed_node/right/image_rect_color/compressed
- /zed2i/zed_node/left/camera_info
- /zed2i/zed_node/right/camera_info

## Why this stage matters
Before evaluating stereo usability, the camera topics must be checked for:
- message presence
- frame identity
- format consistency
- camera_info consistency
- left/right structural compatibility

## Command

```bash
python3 -m scripts.09_inspect_camera
```

# Output Saved
`outputs/tables/camera_image_metadata.csv`
`outputs/tables/camera_info_metadata.csv`

# Interpretations - Initial findings

The stereo camera topics are structurally healthy and suitable for deeper timing and content inspection.

### Image topics
Both left and right compressed image topics are present:
- left images: 2035
- right images: 2028

The image frame_ids are:
- `zed2i_left_camera_optical_frame`
- `zed2i_right_camera_optical_frame`

The recorded image format is consistently:
- `bgra8; jpeg compressed bgr8`

### Camera info topics
Both left and right camera_info topics are also present:
- left camera_info: 4062
- right camera_info: 4023

The camera_info messages are structurally consistent with:
- width: 1024
- height: 576
- distortion model: `rational_polynomial`
- 8 distortion parameters

The sampled intrinsic values appear stable.

### Working interpretation
The camera block is present and structurally usable.
The next step is to inspect timing consistency between left and right images and then inspect sampled image content visually.
