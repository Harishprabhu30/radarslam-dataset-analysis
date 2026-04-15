# 06.2 IMU Frame Alignment Feasibility

## Goal
Check whether the three IMU streams can be transformed into a common frame for direct comparison.

## IMU topics and observed frames

| Topic | frame_id | Notes |
|---|---|---|
| /imu/data | sensor_box/imu_link | external/body IMU candidate |
| /ouster/imu | os_imu | Ouster internal IMU |
| /zed2i/zed_node/imu/data | zed2i_imu_link (expected from ZED chain) | camera internal IMU |

## Why this stage matters
Raw IMU axes cannot be compared directly unless the sensor vectors are expressed in the same coordinate frame.

## Current TF findings
- ZED frame chain is visible in TF
- sensor_box/imu_link appears in TF-related inspection
- Ouster message frame `os_imu` was observed in topic data
- however, the full TF connectivity between `os_imu` and the main body/sensor box frame was not clearly confirmed in the earlier TF snapshot

## Interpretation
Different gravity axes across IMUs do not automatically indicate disagreement.
They most likely indicate different mounting orientations.

A proper comparison requires:
- valid transform from each IMU frame to a common reference frame
- consistent timing
- vector rotation into the common frame

## Current conclusion
At this stage, the dataset supports a conceptual explanation for the IMU differences, but a full transform-based cross-frame comparison is not yet confirmed for all IMUs because the Ouster frame connectivity is incomplete in the current TF evidence.

## Working decision
- treat `/imu/data` and `/zed2i/zed_node/imu/data` as the primary IMUs for later analysis
- treat `/ouster/imu` as a supporting IMU
- postpone full vector-frame comparison until TF connectivity is fully verified

