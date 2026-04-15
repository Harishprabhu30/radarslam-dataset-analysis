from pathlib import Path
from io import BytesIO

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"

LEFT_TOPIC = "/zed2i/zed_node/left/image_rect_color/compressed"
RIGHT_TOPIC = "/zed2i/zed_node/right/image_rect_color/compressed"

PAIRING_INPUT = Path("outputs/tables/camera_stereo_pairing.csv")
TABLE_OUTPUT = Path("outputs/tables/camera_content_sampled.csv")
SAMPLES_DIR = Path("outputs/plots/camera_samples")

MAX_SAMPLE_PAIRS = 12


def choose_sample_indices(total_count: int, max_count: int):
    if total_count <= max_count:
        return list(range(total_count))
    return sorted(set(np.linspace(0, total_count - 1, max_count, dtype=int).tolist()))


def decode_compressed_image(msg):
    img = Image.open(BytesIO(bytes(msg.data))).convert("RGB")
    return np.array(img)


def image_stats(img_rgb: np.ndarray):
    gray = np.dot(img_rgb[..., :3], [0.299, 0.587, 0.114])
    return {
        "height": int(img_rgb.shape[0]),
        "width": int(img_rgb.shape[1]),
        "brightness_mean": float(np.mean(gray)),
        "brightness_std": float(np.std(gray)),
    }


def save_rgb(path: Path, img_rgb: np.ndarray):
    Image.fromarray(img_rgb).save(path)


def save_side_by_side(path: Path, left_rgb: np.ndarray, right_rgb: np.ndarray, title: str):
    plt.figure(figsize=(12, 4))
    plt.suptitle(title)

    plt.subplot(1, 2, 1)
    plt.imshow(left_rgb)
    plt.title("Left")
    plt.axis("off")

    plt.subplot(1, 2, 2)
    plt.imshow(right_rgb)
    plt.title("Right")
    plt.axis("off")

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def open_reader():
    storage_options = rosbag2_py.StorageOptions(uri=BAG_PATH, storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr"
    )
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def load_topic_messages(topic_name: str):
    reader = open_reader()
    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    if topic_name not in type_map:
        raise RuntimeError(f"Missing topic: {topic_name}")

    msg_cls = get_message(type_map[topic_name])

    msgs = []
    while reader.has_next():
        tname, data, bag_timestamp_ns = reader.read_next()
        if tname != topic_name:
            continue

        msg = deserialize_message(data, msg_cls)
        bag_time_s = bag_timestamp_ns / 1e9
        unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
        time_source = get_time_source_label(topic_name, msg)

        msgs.append({
            "topic": topic_name,
            "unified_time_s": unified_time_s,
            "time_source": time_source,
            "msg": msg,
        })

    return msgs


def main():
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    if not PAIRING_INPUT.exists():
        raise FileNotFoundError(f"Missing stereo pairing file: {PAIRING_INPUT}")

    pairing_df = pd.read_csv(PAIRING_INPUT)
    if pairing_df.empty:
        raise RuntimeError("Stereo pairing table is empty.")

    sample_pair_rows = pairing_df.iloc[choose_sample_indices(len(pairing_df), MAX_SAMPLE_PAIRS)].copy()

    left_msgs = load_topic_messages(LEFT_TOPIC)
    right_msgs = load_topic_messages(RIGHT_TOPIC)

    rows = []

    for sample_id, (_, pair_row) in enumerate(sample_pair_rows.iterrows()):
        li = int(pair_row["left_index"])
        ri = int(pair_row["right_index"])
        abs_dt = float(pair_row["abs_time_diff_s"])

        if li >= len(left_msgs) or ri >= len(right_msgs):
            continue

        left_entry = left_msgs[li]
        right_entry = right_msgs[ri]

        left_img = decode_compressed_image(left_entry["msg"])
        right_img = decode_compressed_image(right_entry["msg"])

        left_stats = image_stats(left_img)
        right_stats = image_stats(right_img)

        left_path = SAMPLES_DIR / f"sample_{sample_id:02d}_left.png"
        right_path = SAMPLES_DIR / f"sample_{sample_id:02d}_right.png"
        pair_path = SAMPLES_DIR / f"sample_{sample_id:02d}_pair.png"

        save_rgb(left_path, left_img)
        save_rgb(right_path, right_img)
        save_side_by_side(
            pair_path,
            left_img,
            right_img,
            title=f"Stereo pair sample {sample_id} | |dt|={abs_dt:.6f}s"
        )

        rows.append({
            "sample_id": sample_id,
            "left_index": li,
            "right_index": ri,
            "left_time_s": left_entry["unified_time_s"],
            "right_time_s": right_entry["unified_time_s"],
            "abs_time_diff_s": abs_dt,

            "left_width": left_stats["width"],
            "left_height": left_stats["height"],
            "left_brightness_mean": left_stats["brightness_mean"],
            "left_brightness_std": left_stats["brightness_std"],

            "right_width": right_stats["width"],
            "right_height": right_stats["height"],
            "right_brightness_mean": right_stats["brightness_mean"],
            "right_brightness_std": right_stats["brightness_std"],

            "left_path": str(left_path),
            "right_path": str(right_path),
            "pair_path": str(pair_path),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("No sampled stereo image pairs were saved.")

    df.to_csv(TABLE_OUTPUT, index=False)

    print(f"Saved sampled camera content table to: {TABLE_OUTPUT}")
    print(f"Saved sample images to: {SAMPLES_DIR}")
    print(df[[
        "sample_id",
        "abs_time_diff_s",
        "left_width",
        "left_height",
        "left_brightness_mean",
        "left_brightness_std",
        "right_brightness_mean",
        "right_brightness_std",
    ]].to_string(index=False))


if __name__ == "__main__":
    main()