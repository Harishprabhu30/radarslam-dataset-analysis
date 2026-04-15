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

## What the plots are telling:

### 1. Intensity histogram

**This looks healthy.**

**Interpretation:**

- most returns are in lower-to-mid intensity ranges
- there is a long tail toward higher values
- not all-zero
- not collapsed to one single bin

That suggests the intensity channel is alive and informative.

**So:**

intensity is usable as a supporting LiDAR attribute

### 2. XY scatter plot

**This is the most important visual.**

**What it suggests:**

- the point cloud is not empty
- there is clear radial scan structure
- there are visible surfaces / boundaries / arcs
- there are nearby dense returns and farther sparse returns
- geometry looks like a real scene, not corruption

The circular/radial pattern is expected from LiDAR sampling.  
The visible clusters and boundaries suggest real environment structure.

**So the key conclusion is:**

the cloud looks physically plausible, Not random garbage, not all zeros, not broken.

### 3. Range histogram

**This also looks sensible.**

**Interpretation:**

- many returns are concentrated at shorter ranges
- counts decrease as range increases
- there is a long tail to farther distances

That is a very normal LiDAR behavior pattern.

**One note:**

The numeric scale may look large because the range field may be in a sensor-native unit or scaled integer representation, not necessarily meters.

So document this carefully:

the range distribution is structurally plausible,  
but the exact physical unit of the PointCloud2 `range` field should be verified before using it as metric ground truth.

### 4. Reflectivity histogram

**This also looks healthy.**

**Interpretation:**

- strong concentration at lower reflectivity values
- decaying tail toward higher reflectivity
- no all-zero collapse
- no obviously corrupted spread

So reflectivity is also present and useful.

## CONCLUSION:

The Ouster point clouds are structurally consistent and visually plausible. Sampled frames show realistic scene geometry, and the auxiliary attributes (intensity, reflectivity, range) are populated with meaningful distributions.