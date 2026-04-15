from pathlib import Path
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
OUTPUT_PATH = Path("outputs/tables/imu_all.csv")

IMU_TOPICS = [
    "/imu/data",
    "/ouster/imu",
    "/zed2i/zed_node/imu/data",
]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    storage_options = rosbag2_py.StorageOptions(uri=BAG_PATH, storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    msg_classes = {}
    for topic in IMU_TOPICS:
        if topic not in type_map:
            raise RuntimeError(f"Missing IMU topic in bag: {topic}")
        msg_classes[topic] = get_message(type_map[topic])

    rows = []

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()

        if topic_name not in IMU_TOPICS:
            continue

        msg = deserialize_message(data, msg_classes[topic_name])
        bag_time_s = bag_timestamp_ns / 1e9
        unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
        time_source = get_time_source_label(topic_name, msg)

        row = {
            "imu_topic": topic_name,
            "unified_time_s": unified_time_s,
            "time_source": time_source,
            "bag_time_s": bag_time_s,
            "frame_id": msg.header.frame_id,

            "orientation_x": msg.orientation.x,
            "orientation_y": msg.orientation.y,
            "orientation_z": msg.orientation.z,
            "orientation_w": msg.orientation.w,

            "angular_velocity_x": msg.angular_velocity.x,
            "angular_velocity_y": msg.angular_velocity.y,
            "angular_velocity_z": msg.angular_velocity.z,

            "linear_acceleration_x": msg.linear_acceleration.x,
            "linear_acceleration_y": msg.linear_acceleration.y,
            "linear_acceleration_z": msg.linear_acceleration.z,

            "orientation_cov_00": msg.orientation_covariance[0],
            "orientation_cov_11": msg.orientation_covariance[4],
            "orientation_cov_22": msg.orientation_covariance[8],

            "angular_velocity_cov_00": msg.angular_velocity_covariance[0],
            "angular_velocity_cov_11": msg.angular_velocity_covariance[4],
            "angular_velocity_cov_22": msg.angular_velocity_covariance[8],

            "linear_acceleration_cov_00": msg.linear_acceleration_covariance[0],
            "linear_acceleration_cov_11": msg.linear_acceleration_covariance[4],
            "linear_acceleration_cov_22": msg.linear_acceleration_covariance[8],
        }

        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("No IMU messages extracted.")

    df = df.sort_values(by=["imu_topic", "unified_time_s"]).reset_index(drop=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved IMU extraction to: {OUTPUT_PATH}")
    print(f"Extracted {len(df)} IMU rows total")
    print("\nCounts by topic:")
    print(df["imu_topic"].value_counts().to_string())
    print("\nTime source by topic:")
    print(df.groupby(["imu_topic", "time_source"]).size().to_string())


if __name__ == "__main__":
    main()