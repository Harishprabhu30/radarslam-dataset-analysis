# RADARSLAM Dataset Analysis — Robot and Sensor-System Understanding

A structured analysis repository for understanding a multi-sensor robotic/off-highway dataset recorded in ROS 2 MCAP format.

This repository was built to answer one question before any downstream SLAM, fusion, or evaluation work:

**What is this robot as a sensing system, which sensors can be trusted, and what is the right downstream path?**

---

## Overview

This project analyzes a ROS 2 dataset containing:

- Ouster LiDAR
- Ouster internal IMU
- external IMU
- ZED2i stereo camera
- ZED IMU
- radar detections
- GNSS
- TF and clock topics

The work in this repository is intentionally **staged**.  
Instead of jumping directly into SLAM or fusion, the dataset is first understood in layers:

1. metadata and topic inventory  
2. timing behavior  
3. frame usage  
4. per-sensor structural checks  
5. per-sensor content validation  
6. final trust map and sensor-role summary  

This makes the repository useful not only for analysis, but also for documentation, future reuse, and downstream robotics development.

---

## Main outcome

After the full inspection pipeline, the dataset is best understood as:

- **Primary geometry sensor:** Ouster LiDAR
- **Primary motion sensors:** external IMU and ZED IMU
- **Supporting sensors:** radar and stereo camera
- **Rejected reference sensor:** GNSS

So this dataset should be treated as a:

**LiDAR-IMU-centered perception dataset with supporting radar and visual context**

and **not** as a GNSS-referenced trajectory dataset.

---

## Dataset summary

**Bag format:** MCAP  
**Bag duration:** ~269.34 s  
**Bag size:** ~28.2 GiB

### Main recorded topics

- `/ouster/points`
- `/ouster/scan`
- `/ouster/imu`
- `/imu/data`
- `/zed2i/zed_node/imu/data`
- `/zed2i/zed_node/left/image_rect_color/compressed`
- `/zed2i/zed_node/right/image_rect_color/compressed`
- `/zed2i/zed_node/left/camera_info`
- `/zed2i/zed_node/right/camera_info`
- `/off_highway_premium_radar_sample_driver/locations`
- `/gnss`
- `/tf`
- `/tf_static`
- `/clock`

---

## Repository structure

```text
radarslam-dataset-analysis/
├── README.md
├── data/
│   ├── metadata/
│   │   ├── original_metadata.yaml
│   │   └── ros2_bag_info.txt
│   └── README.md
├── docs/
│   ├── 01_metadata_verification/
│   ├── 02_topic_summary/
│   ├── 03_tf_tree/
│   ├── 04_timing_quality/
│   ├── 04_1_header_vs_bag_timing/
│   ├── 04_2_time_alignment/
│   ├── 05_gnss/
│   ├── 05_1_gnss_diagnostics/
│   ├── 06_imu/
│   ├── 06_1_imu_diagnostics/
│   ├── 06_2_imu_frame_alignment/
│   ├── 07_lidar/
│   ├── 07_1_lidar_diagnostics/
│   ├── 07_2_lidar_content/
│   ├── 08_radar/
│   ├── 08_1_radar_diagnostics/
│   ├── 08_2_radar_content/
│   ├── 09_camera/
│   ├── 09_1_camera_timing/
│   ├── 09_2_camera_content/
│   └── 10_final_robot_understanding/
├── scripts/
│   ├── __init__.py
│   ├── time_utils.py
│   ├── 02_parse_metadata.py
│   ├── 04_timing_analysis.py
│   ├── 04_1_header_vs_bag_timing.py
│   ├── 05_extract_gnss.py
│   ├── 05_1_gnss_diagnostics.py
│   ├── 06_extract_imu.py
│   ├── 06_1_imu_diagnostics.py
│   ├── 07_inspect_lidar.py
│   ├── 07_1_lidar_diagnostics.py
│   ├── 07_2_lidar_content_inspection.py
│   ├── 08_inspect_radar.py
│   ├── 08_1_radar_diagnostics.py
│   ├── 08_2_radar_content_inspection.py
│   ├── 09_inspect_camera.py
│   ├── 09_1_camera_timing.py
│   └── 09_2_camera_content_inspection.py
├── outputs/
│   ├── tables/
│   └── plots/
└── .gitignore

### Analysis stages covered

#### Stage 01 — Metadata verification

Verified the actual bag contents using ros2 bag info and checked them against the provided metadata.

**Main result:**  
Top-level metadata matched bag info, but one file-level message count entry was inconsistent.  
The bag itself was treated as source of truth.

See:

- docs/01_metadata_verification/README.md  
- data/metadata/ros2_bag_info.txt  

---

#### Stage 02 — Topic summary

Built a structured table of all topics, message types, counts, approximate rates, and sensor groups.

See:

- docs/02_topic_summary/README.md  
- outputs/tables/topic_summary.csv  

---

#### Stage 03 — TF and frame inspection

Inspected frame IDs used by sensors and compared them against the available TF graph.

**Main result:**  
Multiple frame families exist, and some sensor chains were only partially confirmed from the recorded TF evidence.

See:

- docs/03_tf_tree/README.md  
- outputs/tf/

### Analysis stages covered

---

#### Stage 04 — Timing analysis

Measured topic timing using bag timestamps.

**Main result:**  
Several topics, especially Ouster-related ones, showed bursty or irregular bag-time spacing.

See:

- docs/04_timing_quality/README.md  
- outputs/tables/topic_timing_summary.csv  

---

#### Stage 04.1 — Header vs bag timestamp comparison

Compared bag timestamps against ROS message header timestamps.

**Main result:**  
The dataset contains two time domains:

- bag record timestamps  
- message header timestamps  

A large constant offset indicated replay or later recording over originally timestamped sensor data.

See:

- docs/04_1_header_vs_bag_timing/README.md  
- outputs/tables/topic_header_vs_bag_timing.csv  

---

#### Stage 04.2 — Unified time policy

Defined a single time-alignment strategy for all later analysis.

**Policy used:**

- use `header.stamp` where valid  
- use shifted bag time for Ouster topics with broken header timestamps  

This logic is implemented in:

- scripts/time_utils.py  

See:

- docs/04_2_time_alignment/README.md  

---

#### Stage 05 — GNSS extraction

Extracted GNSS to a local trajectory representation.

See:

- docs/05_gnss/README.md  
- outputs/tables/gnss_trajectory.csv  

---

#### Stage 05.1 — GNSS diagnostics

Evaluated GNSS trustworthiness.

**Main result:**  
GNSS was rejected due to:

- no-fix status  
- huge covariance  
- unrealistic altitude  
- impossible implied motion speeds  

See:

- docs/05_1_gnss_diagnostics/README.md  
- outputs/tables/gnss_diagnostics_summary.txt  

---

#### Stage 06 — IMU extraction

Extracted all three IMU streams into a unified analysis table.

See:

- docs/06_imu/README.md  
- outputs/tables/imu_all.csv  

---

#### Stage 06.1 — IMU diagnostics

Compared timing, acceleration magnitude, gyro behavior, and gravity consistency.

**Main result:**  
Two strongest IMUs:

- /imu/data  
- /zed2i/zed_node/imu/data  

See:

- docs/06_1_imu_diagnostics/README.md  
- outputs/tables/imu_diagnostics_summary.txt  

---

#### Stage 06.2 — IMU frame-alignment feasibility

Documented why raw IMU axes differ and evaluated whether full common-frame comparison was currently justified.

See:

- docs/06_2_imu_frame_alignment/README.md  

### Stage 07 — LiDAR structural inspection

Inspected /ouster/points and /ouster/scan.

**Main result:**  
LiDAR messages were structurally stable and rich in fields.

See:

- docs/07_lidar/README.md  
- outputs/tables/ouster_points_metadata.csv  
- outputs/tables/ouster_scan_metadata.csv  

---

#### Stage 07.1 — LiDAR diagnostics

Measured message consistency and timing.

**Main result:**  
LiDAR was structurally excellent, though bag-time spacing remained bursty.

See:

- docs/07_1_lidar_diagnostics/README.md  
- outputs/tables/lidar_diagnostics_summary.txt  

---

#### Stage 07.2 — LiDAR content inspection

Sampled real point clouds, validated actual content, and plotted point distributions.

**Main result:**  
LiDAR content is physically plausible and became the strongest primary geometric sensor in the dataset.

See:

- docs/07_2_lidar_content/README.md  
- outputs/tables/ouster_points_content_sampled.csv  
- outputs/plots/ouster_*  

---

### Stage 08 — Radar structural inspection

Inspected radar detections published as PointCloud2.

See:

- docs/08_radar/README.md  
- outputs/tables/radar_metadata.csv  

---

#### Stage 08.1 — Radar diagnostics

Checked timing, point-count variability, and schema stability.

**Main result:**  
Radar is a healthy sparse detection stream with stable structure.

See:

- docs/08_1_radar_diagnostics/README.md  
- outputs/tables/radar_diagnostics_summary.txt  

---

#### Stage 08.2 — Radar content inspection

Sampled radar detections and plotted:

- XY scatter  
- radial velocity  
- RCS  
- SNR  
- point-count distributions  

**Main result:**  
Radar is a valid supporting perception sensor, not a LiDAR replacement.

See:

- docs/08_2_radar_content/README.md  
- outputs/tables/radar_content_sampled.csv  
- outputs/plots/radar_*  

---

### Stage 09 — Camera structural inspection

Inspected stereo image and camera_info topics.

See:

- docs/09_camera/README.md  
- outputs/tables/camera_image_metadata.csv  
- outputs/tables/camera_info_metadata.csv  

---

#### Stage 09.1 — Camera timing and stereo consistency

Measured left/right image timing and nearest-pair consistency.

**Main result:**  
Most stereo pairs were strongly aligned in time and usable for stereo-style use.

See:

- docs/09_1_camera_timing/README.md  
- outputs/tables/camera_timing_summary.txt  
- outputs/tables/camera_stereo_pairing.csv  

---

#### Stage 09.2 — Camera sampled image inspection

Decoded sampled stereo pairs and inspected their visual content.

**Main result:**  
Camera images are visually usable and stereo-consistent, but both channels appear upside down, likely due to mounting orientation or missing rotation correction.

See:

- docs/09_2_camera_content/README.md  
- outputs/tables/camera_content_sampled.csv  
- outputs/plots/camera_samples/  

---

### Stage 10 — Final robot and sensor-system understanding

Final synthesis of the whole dataset.

See:

- docs/10_final_robot_understanding/README.md  
- outputs/tables/final_sensor_trust_map.csv (optional if you create it)  

---

### Final sensor trust map

#### Primary trusted sensors
- /ouster/points  
- /imu/data  
- /zed2i/zed_node/imu/data  

#### Secondary / supporting sensors
- /off_highway_premium_radar_sample_driver/locations  
- stereo camera topics  
- /ouster/imu  
- /ouster/scan  

#### Rejected
- /gnss  

### Key interesting facts

- The dataset contains dual time domains and required an explicit unified time policy.  
- Ouster header timestamps were not reliable and had to be handled differently.  
- GNSS existed in the bag but was fully rejected as a trusted reference.  
- The stereo camera is usable but appears upside down in both channels, which strongly suggests mounting inversion or missing orientation correction.  
- Radar is much richer than a plain XYZ cloud and includes velocity, uncertainty, SNR, and RCS-like attributes.  
- LiDAR turned out to be the strongest and most trustworthy geometric sensing block.

### Recommended downstream direction

The strongest next technical branch is:

**LiDAR + IMU centered downstream work**

---

### Most practical combinations:

- LiDAR + external IMU  
- LiDAR + ZED IMU  

---

### Supporting combinations:

- LiDAR + radar  
- LiDAR + stereo camera  

---

### Not recommended:

- any pipeline relying on GNSS as trusted reference

### How to inspect the results

#### Read the docs

The main story is documented stage-by-stage under:

**docs/**

---

#### The best places to start are:

- docs/10_final_robot_understanding/README.md  
- docs/04_2_time_alignment/README.md  
- docs/07_2_lidar_content/README.md  
- docs/08_2_radar_content/README.md  
- docs/09_2_camera_content/README.md  

### Inspect tables

Structured outputs are under:

**outputs/tables/**

Useful files include:

- topic_summary.csv  
- topic_timing_summary.csv  
- topic_header_vs_bag_timing.csv  
- gnss_diagnostics_summary.txt  
- imu_all.csv  
- imu_diagnostics_summary.txt  
- lidar_diagnostics_summary.txt  
- ouster_points_content_sampled.csv  
- radar_diagnostics_summary.txt  
- radar_content_sampled.csv  
- camera_timing_summary.txt  
- camera_content_sampled.csv  

---

### Inspect plots

Plots are under:

**outputs/plots/**

Especially:

- ouster_*  
- radar_*  
- camera_samples/*  

### Requirements

This repository expects:

- Python 3.10+  
- ROS 2 environment with `rosbag2_py`  
- `rclpy`  
- `rosidl_runtime_py`  
- `sensor_msgs_py`  
- `numpy`  
- `pandas`  
- `matplotlib`  
- `Pillow`  
- `PyYAML`  

---

A virtual environment is recommended.

### Setup

#### 1. Clone the repository

```bash
git clone https://github.com/Harishprabhu30/radarslam-dataset-analysis.git
cd radarslam-dataset-analysis
```

#### 2. Source ROS 2 before running scripts and python venv

```bash
source /opt/ros/humble/setup.bash
```

#### 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 4. Install requirements.txt

Inside the created virtual environment:

```bash
pip install -r requirements.txt
```

### Data placement

Place the raw MCAP bag in the expected raw-data location used by the scripts, for example:

```bash
/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap
```

### How to run

The repository was designed so each stage can be run independently.

---

### Examples:

```bash
python3 -m scripts.02_parse_metadata
python3 -m scripts.04_timing_analysis
python3 -m scripts.04_1_header_vs_bag_timing
python3 -m scripts.05_extract_gnss
python3 -m scripts.05_1_gnss_diagnostics
python3 -m scripts.06_extract_imu
python3 -m scripts.06_1_imu_diagnostics
python3 -m scripts.07_inspect_lidar
python3 -m scripts.07_1_lidar_diagnostics
python3 -m scripts.07_2_lidar_content_inspection
python3 -m scripts.08_inspect_radar
python3 -m scripts.08_1_radar_diagnostics
python3 -m scripts.08_2_radar_content_inspection
python3 -m scripts.09_inspect_camera
python3 -m scripts.09_1_camera_timing
python3 -m scripts.09_2_camera_content_inspection

### Reproducibility notes

- The analysis uses a document-first structure.  
- Each stage has its own `README.md`.  
- Outputs are separated into tables and plots.  
- Time handling is centralized in `scripts/time_utils.py`.  
- The repository intentionally avoids blindly trusting all recorded topics.  

### Future directions

This repository now supports several downstream paths:

---

#### 1. LiDAR + IMU downstream preparation

Build a trusted subset centered on:

- /ouster/points  
- /imu/data  
- /zed2i/zed_node/imu/data  

---

#### 2. Curated benchmark export

Prepare cleaned exports and standard aligned tables for future experiments.

---

#### 3. Radar-support branch

Study radar as a sparse supporting perception source.

---

#### 4. Stereo-support branch

Explore stereo feasibility after handling the camera’s 180° orientation.

---

#### 5. Fusion-readiness branch

Formalize trusted combinations, frame assumptions, and timing policy for later fusion experiments.

### Maintainer note

This repository is intentionally built to answer what the robot is and how its sensors should be trusted before attempting deeper SLAM, fusion, or estimation work.