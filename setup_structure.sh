# !/bin/bash

set -e # to stop on error

echo "Creating project structure inside current directory..."

# create dictories 
mkdir -p raw/data
mkdir -p data/metadata
mkdir -p docs 
mkdir -p scripts
mkdir -p outputs/{tables,plots,tf,logs}
mkdir -p notebooks
mkdir -p config

# data files
touch data/README.md
touch data/metadata/original_metadata.yaml
touch data/metadata/ros2_bag_info.txt

# Docs
touch docs/00_dataset_identity.md
touch docs/01_metadata_check.md
touch docs/02_topic_summary.md
touch docs/03_tf_tree.md
touch docs/04_sensor_timing.md
touch docs/05_gnss.md
touch docs/06_imu_comparison.md
touch docs/07_lidar.md
touch docs/08_radar.md
touch docs/09_camera.md

# Scripts
touch scripts/01_bag_info_check.sh
touch scripts/02_parse_metadata.py
touch scripts/03_topic_rate_analysis.py
touch scripts/04_extract_tf_tree.py
touch scripts/05_extract_gnss.py
touch scripts/06_extract_imu.py
touch scripts/07_lidar_sanity.py
touch scripts/08_radar_fields.py
touch scripts/09_camera_sync_check.py

# Notebooks
touch notebooks/exploration.ipynb

# Config
touch config/dataset_config.yaml

echo "Done!"