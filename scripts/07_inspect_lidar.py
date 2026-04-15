from pathlib import Path
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"

POINTS_TOPIC = "/ouster/points"
SCAN_TOPIC = "/ouster/scan"

OUTPUT_POINTS_META = Path("outputs/tables/ouster_points_metadata.csv")
OUTPUT_SCAN_META = Path("outputs/tables/ouster_scan_metadata.csv")


def main():
    OUTPUT_POINTS_META.parent.mkdir(parents=True, exist_ok=True)

    storage_options = rosbag2_py.StorageOptions(uri=BAG_PATH, storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    if POINTS_TOPIC not in type_map:
        raise RuntimeError(f"Missing topic: {POINTS_TOPIC}")
    if SCAN_TOPIC not in type_map:
        raise RuntimeError(f"Missing topic: {SCAN_TOPIC}")

    points_cls = get_message(type_map[POINTS_TOPIC])
    scan_cls = get_message(type_map[SCAN_TOPIC])

    point_rows = []
    scan_rows = []

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()
        bag_time_s = bag_timestamp_ns / 1e9

        if topic_name == POINTS_TOPIC:
            msg = deserialize_message(data, points_cls)
            unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
            time_source = get_time_source_label(topic_name, msg)

            field_names = [f.name for f in msg.fields]
            estimated_point_count = msg.width * msg.height

            point_rows.append({
                "topic": topic_name,
                "unified_time_s": unified_time_s,
                "time_source": time_source,
                "frame_id": msg.header.frame_id,
                "height": msg.height,
                "width": msg.width,
                "estimated_point_count": estimated_point_count,
                "field_count": len(msg.fields),
                "field_names": ",".join(field_names),
                "is_bigendian": msg.is_bigendian,
                "point_step": msg.point_step,
                "row_step": msg.row_step,
                "is_dense": msg.is_dense,
                "data_length_bytes": len(msg.data),
            })

        elif topic_name == SCAN_TOPIC:
            msg = deserialize_message(data, scan_cls)
            unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
            time_source = get_time_source_label(topic_name, msg)

            scan_rows.append({
                "topic": topic_name,
                "unified_time_s": unified_time_s,
                "time_source": time_source,
                "frame_id": msg.header.frame_id,
                "angle_min": msg.angle_min,
                "angle_max": msg.angle_max,
                "angle_increment": msg.angle_increment,
                "time_increment": msg.time_increment,
                "scan_time": msg.scan_time,
                "range_min": msg.range_min,
                "range_max": msg.range_max,
                "ranges_count": len(msg.ranges),
                "intensities_count": len(msg.intensities),
            })

    df_points = pd.DataFrame(point_rows)
    df_scan = pd.DataFrame(scan_rows)

    if df_points.empty:
        raise RuntimeError("No /ouster/points messages extracted.")
    if df_scan.empty:
        raise RuntimeError("No /ouster/scan messages extracted.")

    df_points.to_csv(OUTPUT_POINTS_META, index=False)
    df_scan.to_csv(OUTPUT_SCAN_META, index=False)

    print(f"Saved points metadata to: {OUTPUT_POINTS_META}")
    print(f"Saved scan metadata to: {OUTPUT_SCAN_META}")
    print("\n/ ouster/points sample summary:")
    print(df_points.head().to_string(index=False))
    print("\n/ ouster/scan sample summary:")
    print(df_scan.head().to_string(index=False))


if __name__ == "__main__":
    main()