#!/bin/bash

# ROS 2 Bag Info Script

BAG_PATH="/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
OUTPUT_DIR="/workspace/data/metadata"
OUTPUT_FILE="$OUTPUT_DIR/ros2_bag_info.txt"

echo "Creating output directory..."
mkdir -p "$OUTPUT_DIR"

echo "Running ros2 bag info..."
ros2 bag info "$BAG_PATH" | tee "$OUTPUT_FILE"

echo "Done!"
echo "Saved to: $OUTPUT_FILE"