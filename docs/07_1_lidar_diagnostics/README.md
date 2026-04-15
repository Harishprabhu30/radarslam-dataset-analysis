# 07.1 LiDAR Diagnostics

## Goal
Evaluate structural consistency and timing stability of the Ouster LiDAR topics.

## Inputs
- `outputs/tables/ouster_points_metadata.csv`
- `outputs/tables/ouster_scan_metadata.csv`

## Diagnostics performed
- frame count
- uniqueness of frame_id and field structure
- point count consistency
- data size consistency
- dt statistics
- scan structure consistency

## Command

```bash
python3 -m scripts.07_1_lidar_diagnostics
```

# Output
`outputs/tables/lidar_diagnostics_summary.txt`

## Final conclusion

The Ouster LiDAR topics are structurally highly consistent and suitable for later geometric analysis.

### /ouster/points
The 3D point cloud stream shows:
- constant frame identity
- constant field structure
- constant point count (65536)
- constant message size
- no structural variation across frames

This indicates a strong and reliable LiDAR data stream for offline analysis.

### /ouster/scan
The projected 2D scan stream also shows:
- constant frame identity
- constant number of ranges and intensities
- constant scan time
- constant range limits

### Timing note
Bag-time spacing is irregular for both `/ouster/points` and `/ouster/scan`, with median dt much smaller than mean dt and occasional long pauses.

This is consistent with earlier findings that Ouster timing should not be interpreted as a clean real-time acquisition clock from bag timestamps alone.

### Working decision
`/ouster/points` should be treated as the primary LiDAR topic for later analysis.
`/ouster/scan` should be treated as a secondary simplified LiDAR representation.

** Goto docs/07_2_lidar_content/README.md to know more on whats inside the Lidar.