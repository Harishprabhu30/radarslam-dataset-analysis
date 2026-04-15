from pathlib import Path
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"

LEFT_IMAGE_TOPIC = "/zed2i/zed_node/left/image_rect_color/compressed"
RIGHT_IMAGE_TOPIC = "/zed2i/zed_node/right/image_rect_color/compressed"
LEFT_INFO_TOPIC = "/zed2i/zed_node/left/camera_info"
RIGHT_INFO_TOPIC = "/zed2i/zed_node/right/camera_info"

OUTPUT_IMAGES = Path("outputs/tables/camera_image_metadata.csv")
OUTPUT_INFO = Path("outputs/tables/camera_info_metadata.csv")


def main():
    OUTPUT_IMAGES.parent.mkdir(parents=True, exist_ok=True)

    storage_options = rosbag2_py.StorageOptions(uri=BAG_PATH, storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )

    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)

    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    needed_topics = [
        LEFT_IMAGE_TOPIC, RIGHT_IMAGE_TOPIC,
        LEFT_INFO_TOPIC, RIGHT_INFO_TOPIC
    ]
    for topic in needed_topics:
        if topic not in type_map:
            raise RuntimeError(f"Missing topic: {topic}")

    msg_classes = {topic: get_message(type_map[topic]) for topic in needed_topics}

    image_rows = []
    info_rows = []

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()

        if topic_name not in needed_topics:
            continue

        msg = deserialize_message(data, msg_classes[topic_name])
        bag_time_s = bag_timestamp_ns / 1e9
        unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
        time_source = get_time_source_label(topic_name, msg)

        if topic_name in [LEFT_IMAGE_TOPIC, RIGHT_IMAGE_TOPIC]:
            image_rows.append({
                "topic": topic_name,
                "unified_time_s": unified_time_s,
                "time_source": time_source,
                "frame_id": msg.header.frame_id,
                "format": msg.format,
                "data_length_bytes": len(msg.data),
            })

        elif topic_name in [LEFT_INFO_TOPIC, RIGHT_INFO_TOPIC]:
            info_rows.append({
                "topic": topic_name,
                "unified_time_s": unified_time_s,
                "time_source": time_source,
                "frame_id": msg.header.frame_id,
                "height": msg.height,
                "width": msg.width,
                "distortion_model": msg.distortion_model,
                "d_len": len(msg.d),
                "k_00": msg.k[0],
                "k_11": msg.k[4],
                "k_02": msg.k[2],
                "k_12": msg.k[5],
                "p_00": msg.p[0],
                "p_11": msg.p[5],
                "p_02": msg.p[2],
                "p_12": msg.p[6],
            })

    df_images = pd.DataFrame(image_rows)
    df_info = pd.DataFrame(info_rows)

    if df_images.empty:
        raise RuntimeError("No compressed image messages extracted.")
    if df_info.empty:
        raise RuntimeError("No camera_info messages extracted.")

    df_images.to_csv(OUTPUT_IMAGES, index=False)
    df_info.to_csv(OUTPUT_INFO, index=False)

    print(f"Saved image metadata to: {OUTPUT_IMAGES}")
    print(f"Saved camera_info metadata to: {OUTPUT_INFO}")
    print("\nImage topic counts:")
    print(df_images["topic"].value_counts().to_string())
    print("\nCamera info topic counts:")
    print(df_info["topic"].value_counts().to_string())
    print("\nImage metadata sample:")
    print(df_images.head().to_string(index=False))
    print("\nCamera info sample:")
    print(df_info.head().to_string(index=False))


if __name__ == "__main__":
    main()

    