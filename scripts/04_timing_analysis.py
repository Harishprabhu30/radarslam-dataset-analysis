from pathlib import Path
from statistics import mean, median
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
OUTPUT_PATH = Path("outputs/tables/topic_timing_summary.csv")

TARGET_TOPICS = [
    "/ouster/points",
    "/ouster/imu",
    "/imu/data",
    "/gnss",
    "/off_highway_premium_radar_sample_driver/locations",
    "/zed2i/zed_node/left/image_rect_color/compressed",
    "/zed2i/zed_node/right/image_rect_color/compressed",
    "/zed2i/zed_node/imu/data",
    "/ouster/scan",
    "/tf",
    "/tf_static",
]

BAG_DURATION_S = 269.341840121


def safe_stats(times_ns):
    if len(times_ns) < 2:
        return {
            "first_timestamp_s": times_ns[0] / 1e9 if times_ns else None,
            "last_timestamp_s": times_ns[0] / 1e9 if times_ns else None,
            "topic_duration_s": 0.0,
            "mean_dt_s": None,
            "median_dt_s": None,
            "min_dt_s": None,
            "max_dt_s": None,
            "approx_true_hz": None,
            "irregularity_ratio": None,
        }

    times_s = [t / 1e9 for t in times_ns]
    dts = [times_s[i] - times_s[i - 1] for i in range(1, len(times_s))]

    topic_duration_s = times_s[-1] - times_s[0]
    mean_dt_s = mean(dts)
    median_dt_s = median(dts)
    min_dt_s = min(dts)
    max_dt_s = max(dts)
    approx_true_hz = (len(times_s) - 1) / topic_duration_s if topic_duration_s > 0 else None
    irregularity_ratio = max_dt_s / median_dt_s if median_dt_s and median_dt_s > 0 else None

    return {
        "first_timestamp_s": round(times_s[0], 6),
        "last_timestamp_s": round(times_s[-1], 6),
        "topic_duration_s": round(topic_duration_s, 6),
        "mean_dt_s": round(mean_dt_s, 6),
        "median_dt_s": round(median_dt_s, 6),
        "min_dt_s": round(min_dt_s, 6),
        "max_dt_s": round(max_dt_s, 6),
        "approx_true_hz": round(approx_true_hz, 3) if approx_true_hz is not None else None,
        "irregularity_ratio": round(irregularity_ratio, 3) if irregularity_ratio is not None else None,
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    storage_options = rosbag2_py.StorageOptions(
        uri=BAG_PATH,
        storage_id="mcap"
    )
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    timestamps_by_topic = {topic: [] for topic in TARGET_TOPICS}

    while reader.has_next():
        topic_name, data, timestamp_ns = reader.read_next()
        if topic_name in timestamps_by_topic:
            timestamps_by_topic[topic_name].append(timestamp_ns)

    rows = []

    for topic in TARGET_TOPICS:
        times_ns = timestamps_by_topic.get(topic, [])
        count = len(times_ns)
        expected_hz_from_bag_duration = count / BAG_DURATION_S if BAG_DURATION_S > 0 else None

        row = {
            "topic": topic,
            "type": type_map.get(topic, "unknown"),
            "message_count_read": count,
            "expected_hz_from_bag_duration": round(expected_hz_from_bag_duration, 3) if expected_hz_from_bag_duration else None,
        }
        row.update(safe_stats(times_ns))
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values(by="topic")
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved timing summary to: {OUTPUT_PATH}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()