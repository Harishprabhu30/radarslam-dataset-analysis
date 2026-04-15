from pathlib import Path
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
RADAR_TOPIC = "/off_highway_premium_radar_sample_driver/locations"

OUTPUT_PATH = Path("outputs/tables/radar_metadata.csv")


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

    if RADAR_TOPIC not in type_map:
        raise RuntimeError(f"Missing topic: {RADAR_TOPIC}")

    msg_cls = get_message(type_map[RADAR_TOPIC])

    rows = []

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()

        if topic_name != RADAR_TOPIC:
            continue

        msg = deserialize_message(data, msg_cls)
        bag_time_s = bag_timestamp_ns / 1e9
        unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
        time_source = get_time_source_label(topic_name, msg)

        field_names = [f.name for f in msg.fields]
        estimated_point_count = msg.width * msg.height

        rows.append({
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

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("No radar messages extracted.")

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved radar metadata to: {OUTPUT_PATH}")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()