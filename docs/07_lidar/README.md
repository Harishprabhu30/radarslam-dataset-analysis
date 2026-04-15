# 07 LiDAR Structural Inspection

## Goal
Inspect the Ouster LiDAR topics structurally before deeper point cloud analysis.

## Topics analysed
- /ouster/points
- /ouster/scan

## Why this stage matters
Before computing LiDAR statistics or extracting frames, the dataset should be checked for:
- frame identity
- field structure
- point count consistency
- scan structure
- timing source

## Outputs
- `outputs/tables/ouster_points_metadata.csv`
- `outputs/tables/ouster_scan_metadata.csv`

## Command

```bash
python3 -m scripts.07_inspect_lidar
```

## Initial findings

The Ouster LiDAR topics are structurally well-formed and suitable for further analysis.

### /ouster/points
The 3D point cloud is an organized cloud with:
- frame_id: `os_lidar`
- height: 128
- width: 512
- estimated point count: 65536 per cloud

Available fields:
- x, y, z
- intensity
- t
- reflectivity
- ring
- ambient
- range

This indicates a rich LiDAR stream suitable for point cloud quality analysis and later mapping/localization work.

### /ouster/scan
The projected 2D scan is also structurally consistent:
- frame_id: `os_lidar`
- full 360° angular span
- 512 range samples
- scan_time: 0.05 s
- range limits: 0.1 m to 120.0 m

### Working interpretation
`/ouster/points` should be treated as the main LiDAR topic.
`/ouster/scan` should be treated as a secondary simplified representation.

