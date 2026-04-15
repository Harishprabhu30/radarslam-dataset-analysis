# 08 Radar Structural Inspection

## Goal
Inspect the radar detections topic structurally before deeper content analysis.

## Topic analysed
- `/off_highway_premium_radar_sample_driver/locations`

## Why this stage matters
The radar topic is published as `sensor_msgs/PointCloud2`, but radar point clouds are usually sparse and semantically different from LiDAR point clouds.
Before deeper analysis, the message structure, field layout, and point count behavior need to be verified.

## Command

```bash
python3 -m scripts.08_inspect_radar
```

# Output Saved:
`outputs/tables/radar_metadata.csv`

## Initial findings

The radar detections topic is structurally healthy and semantically richer than a simple XYZ point cloud.

### Message structure
The topic is published as `sensor_msgs/PointCloud2` with:
- `frame_id = base_link`
- `height = 1`
- variable `width` per frame
- constant `point_step = 80`
- internally consistent `row_step = width × point_step`

This indicates a flat list of radar detections per message rather than a dense organized cloud.

### Detection count behavior
The number of detections varies from frame to frame, which is expected for radar.
Unlike LiDAR, radar returns are sparse and object-dependent, so variable point count is a normal behavior rather than a fault.

### Available per-point attributes
The radar detections provide rich fields including:
- position (`x, y, z`)
- radial distance
- radial velocity
- azimuth and elevation angles
- radar cross section
- signal-to-noise ratio
- variance and probability fields
- measurement status information

### Working interpretation
The radar topic appears structurally suitable for deeper content analysis.
It should be treated as a sparse, detection-oriented supporting sensor rather than a dense geometric sensor like LiDAR.

** GOTO docs/08_1_radar_diagnostics/README.md to know more about radar.
