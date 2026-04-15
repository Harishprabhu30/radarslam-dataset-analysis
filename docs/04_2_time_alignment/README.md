# 04.2 Time Alignment Strategy

## Goal
Define a single unified time policy for all later analysis scripts.

## Why this stage is needed
The dataset contains two time domains:

- bag record timestamps
- ROS message header timestamps

For several topics, these time domains differ by a large constant offset.
This indicates that the bag was recorded or replayed at a later time than the original sensor acquisition.

Because of this, later analysis must not mix raw bag timestamps and raw header timestamps directly.

## Master time policy
The unified timeline for this dataset is defined in the **header timestamp domain**.

This was chosen because the following topics show valid and consistent header timing:

- /gnss
- /imu/data
- /off_highway_premium_radar_sample_driver/locations
- /zed2i/zed_node/imu/data
- /zed2i/zed_node/left/image_rect_color/compressed
- /zed2i/zed_node/right/image_rect_color/compressed

## Ouster exception
The following Ouster topics showed invalid or inconsistent header timing:

- /ouster/imu
- /ouster/points
- /ouster/scan

For these topics, bag timestamps are used as the source time and converted into the master timeline using a constant offset.

## Alignment rule
For topics with valid header timestamps:

`unified_time = header_time`

For Ouster topics:

`unified_time = bag_time - TIME_OFFSET_S`

## Current offset estimate
A near-constant offset was observed:

`TIME_OFFSET_S ≈ 18582410.0`

This value may be refined later if a better cross-sensor alignment reference is identified.

## Practical rule for all later scripts
All extraction and analysis scripts must output time in the unified timeline.

This means:
- use header time when valid
- use converted bag time for Ouster topics
- do not mix raw bag time and raw header time in final analysis tables

## Limitation
The Ouster alignment currently uses a constant offset assumption.
This is acceptable for initial offline analysis, but may need refinement if sub-frame synchronization becomes important later.

## The file is added and will be called inside the analysis code files to time align to header stamps.