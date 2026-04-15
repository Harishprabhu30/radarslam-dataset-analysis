from pathlib import Path
from statistics import mean, median
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
OUTPUT_PATH = Path("outputs/tables/topic_header_vs_bag_timing.csv")

TARGET_TOPICS = [
    "/gnss",
    "/imu/data",
    "/off_highway_premium_radar_sample_driver/locations",
    "/ouster/imu",
    "/ouster/points",
    "/ouster/scan",
    "/zed2i/zed_node/imu/data",
    "/zed2i/zed_node/left/image_rect_color/compressed",
    "/zed2i/zed_node/right/image_rect_color/compressed",
]


def stamp_to_sec(stamp):
    return stamp.sec + stamp.nanosec * 1e-9


def compute_time_stats(times_s):
    if len(times_s) < 2:
        return {
            "first_s": times_s[0] if times_s else None,
            "last_s": times_s[0] if times_s else None,
            "duration_s": 0.0 if times_s else None,
            "mean_dt_s": None,
            "median_dt_s": None,
            "min_dt_s": None,
            "max_dt_s": None,
            "approx_hz": None,
            "irregularity_ratio": None,
        }

    dts = [times_s[i] - times_s[i - 1] for i in range(1, len(times_s))]
    duration_s = times_s[-1] - times_s[0]
    mean_dt = mean(dts)
    median_dt = median(dts)
    min_dt = min(dts)
    max_dt = max(dts)
    approx_hz = (len(times_s) - 1) / duration_s if duration_s > 0 else None
    irregularity_ratio = max_dt / median_dt if median_dt and median_dt > 0 else None

    return {
        "first_s": round(times_s[0], 6),
        "last_s": round(times_s[-1], 6),
        "duration_s": round(duration_s, 6),
        "mean_dt_s": round(mean_dt, 6),
        "median_dt_s": round(median_dt, 6),
        "min_dt_s": round(min_dt, 6),
        "max_dt_s": round(max_dt, 6),
        "approx_hz": round(approx_hz, 3) if approx_hz is not None else None,
        "irregularity_ratio": round(irregularity_ratio, 3) if irregularity_ratio is not None else None,
    }


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

    bag_times = {topic: [] for topic in TARGET_TOPICS}
    header_times = {topic: [] for topic in TARGET_TOPICS}

    msg_classes = {}
    for topic in TARGET_TOPICS:
        if topic in type_map:
            msg_classes[topic] = get_message(type_map[topic])

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()

        if topic_name not in TARGET_TOPICS:
            continue

        bag_time_s = bag_timestamp_ns / 1e9
        bag_times[topic_name].append(bag_time_s)

        try:
            msg_type = msg_classes[topic_name]
            msg = deserialize_message(data, msg_type)

            if hasattr(msg, "header") and hasattr(msg.header, "stamp"):
                header_time_s = stamp_to_sec(msg.header.stamp)
                header_times[topic_name].append(header_time_s)

        except Exception as e:
            print(f"Warning: failed to parse {topic_name}: {e}")

    rows = []

    for topic in TARGET_TOPICS:
        row = {
            "topic": topic,
            "type": type_map.get(topic, "unknown"),
            "count": len(bag_times[topic]),
        }

        bag_stats = compute_time_stats(bag_times[topic])
        header_stats = compute_time_stats(header_times[topic])

        for k, v in bag_stats.items():
            row[f"bag_{k}"] = v

        for k, v in header_stats.items():
            row[f"header_{k}"] = v

        if bag_times[topic] and header_times[topic]:
            row["start_offset_bag_minus_header_s"] = round(
                bag_times[topic][0] - header_times[topic][0], 6
            )
            row["end_offset_bag_minus_header_s"] = round(
                bag_times[topic][-1] - header_times[topic][-1], 6
            )
        else:
            row["start_offset_bag_minus_header_s"] = None
            row["end_offset_bag_minus_header_s"] = None

        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values(by="topic")
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved comparison table to: {OUTPUT_PATH}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()