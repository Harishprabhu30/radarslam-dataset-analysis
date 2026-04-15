# 07.2 LiDAR Content Inspection

## Goal
Inspect the actual content of sampled `/ouster/points` frames beyond message structure.

## Why this stage matters
A LiDAR stream may be structurally consistent but still contain invalid points, sparse returns, or unrealistic values.
This stage checks actual point content and saves lightweight visual plots.

## Sampling strategy
A limited number of LiDAR frames are sampled across the bag to keep inspection lightweight while covering early, middle, and late parts of the recording.

## Diagnostics performed
- decoded point count
- valid vs invalid XYZ count
- valid ratio
- XYZ min/max
- range statistics
- intensity statistics
- reflectivity statistics
- ambient statistics
- ring coverage

## Plots produced
- XY top-view scatter for selected sampled frames
- aggregated range histogram
- aggregated intensity histogram
- aggregated reflectivity histogram

## Command

```bash
python3 -m scripts.07_2_lidar_content_inspection
```

# Output Saved:
`outputs/tables/ouster_points_content_sampled.csv`
`outputs/plots/ouster_points_xy_sample_*.png`
`outputs/plots/ouster_range_hist.png`
`outputs/plots/ouster_intensity_hist.png`
`outputs/plots/ouster_reflectivity_hist.png`