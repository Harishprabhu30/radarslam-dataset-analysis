# 04 Timing Quality Analysis

## Goal
Measure the real timing behavior of important topics in the MCAP dataset.

## Why this stage matters
Topic counts alone are not enough. A topic may have the expected number of messages but still contain pauses, jitter, or irregular timing.

## Metrics used

- first timestamp
- last timestamp
- topic active duration
- mean inter-message interval
- median inter-message interval
- minimum interval
- maximum interval
- estimated true topic frequency
- expected frequency from full bag duration
- irregularity ratio = max_dt / median_dt

## Command used

```bash
python3 scripts/04_timing_analysis.py
'''

## Output
'''bash
outputs/tables/topic_timing_summary.csv
'''

## Key Observations

The timing summary was computed using bag record timestamps, not ROS message header timestamps.

This revealed that several topics have a large gap between mean inter-message interval and median inter-message interval. For example:

- `/ouster/imu`: mean dt is much larger than median dt
- `/ouster/points`: median dt is much smaller than expected LiDAR frame period
- `/ouster/scan`: median dt is extremely small compared to mean dt
- `/imu/data`: median dt is much smaller than expected for a 50 Hz IMU

This suggests that bag record time may include bursty write behavior or transport-level grouping, and therefore bag timestamps alone are not sufficient to describe the true sensor timing characteristics.

Because of this, a follow-up stage is required to compare:
- bag record timestamp
- message header timestamp

This comparison will help determine whether the irregularity is caused by the sensor stream itself or by recording behavior.

## Initial Interpretation

- GNSS looks relatively plausible near 2 Hz, though with some irregularity.
- Camera and radar topics look roughly consistent with ~7.8 Hz operation, but still show noticeable gaps.
- Ouster and IMU-related topics show strong signs of burst-like or non-uniform bag timestamp spacing.
- A header timestamp comparison is required before drawing conclusions about true sensor timing quality.

### Next performing header timstamp vs bag timestamp analysis. see script : scripts/04_1_header_vs_bag_timing.py