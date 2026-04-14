# 01 Metadata Verification

## Goal
Verify whether the provided `metadata.yaml` matches the actual MCAP bag.

## Command Used

```bash
ros2 bag info rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap

### Confirmed Values

| Field              | metadata.yaml        | ros2 bag info        | Status        |
|--------------------|---------------------|----------------------|--------------|
| Storage ID         | mcap                | mcap                 | Match        |
| Duration           | 269.341840121 s     | 269.341840121 s      | Match        |
| Start time         | 1771336702.019784762| 1771336702.019784762 | Match        |
| Message count      | 216175              | 216175               | Match        |
| File message count | 412251              | Not confirmed        | Inconsistent |
| Bag size           | Not listed          | 28.2 GiB             | Confirmed from bag info |

# Observation

The top-level message count in metadata.yaml matches ros2 bag info.
However, the file-level message count shows 412251, which does not match the actual bag info output.

# Decision

Use MCAP and ros2 bag info as the source of truth. Treat 216175 as the valid message count.


## What to do next

Next step is **Stage 2: topic summary table**.

Make a table with:

```text
topic
message type
count
approx rate = count / 269.341840121
sensor group
analysis use

