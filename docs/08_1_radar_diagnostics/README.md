# 08.1 Radar Diagnostics

## Goal
Evaluate timing and structural consistency of the radar detections topic.

## Input
`outputs/tables/radar_metadata.csv`

## Diagnostics performed
- frame count
- unique frame and field structure checks
- dt statistics
- detection count statistics
- message size statistics

## Command

```bash
python3 -m scripts.08_1_radar_diagnostics
```

# Outputs Saved
`outputs/tables/radar_diagnostics_summary.txt`

## Final conclusion

The radar detections topic is structurally consistent and operationally plausible.

### Structure
The message layout is fully stable across the dataset:
- one consistent frame_id
- one consistent field schema
- one consistent point format

### Timing
Radar timing is much cleaner than the bag-timestamp behavior observed for Ouster topics.
The stream runs at roughly 8 Hz on average, with some irregular gaps.

### Detection count behavior
The number of detections varies substantially from frame to frame, which is expected for radar.
This is consistent with radar functioning as a sparse, scene-dependent detection sensor rather than a dense scanning sensor.

### Working decision
The radar stream is suitable for deeper content inspection and should be treated as a valid supporting sensor in the dataset.

** GOTO docs/08_2_radar_content/README.md to know more in depth of the content of radar.
