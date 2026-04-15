from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message
from sensor_msgs_py import point_cloud2

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
RADAR_TOPIC = "/off_highway_premium_radar_sample_driver/locations"

TABLE_OUTPUT = Path("outputs/tables/radar_content_sampled.csv")
PLOTS_DIR = Path("outputs/plots")

MAX_ANALYSIS_FRAMES = 30
SCATTER_FRAME_COUNT = 3


def choose_sample_indices(total_count: int, max_frames: int):
    if total_count <= max_frames:
        return list(range(total_count))
    return sorted(set(np.linspace(0, total_count - 1, max_frames, dtype=int).tolist()))


def choose_scatter_positions(sampled_count: int):
    if sampled_count <= 1:
        return [0]
    if sampled_count == 2:
        return [0, 1]
    return sorted(set([0, sampled_count // 2, sampled_count - 1]))


def save_hist(data, xlabel, title, path):
    plt.figure(figsize=(8, 5))
    plt.hist(data, bins=50)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_xy_scatter(x, y, title, path):
    plt.figure(figsize=(7, 7))
    plt.scatter(x, y, s=8)
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title(title)
    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def open_reader():
    storage_options = rosbag2_py.StorageOptions(uri=BAG_PATH, storage_id="mcap")
    converter_options = rosbag2_py.ConverterOptions(
        input_serialization_format="cdr",
        output_serialization_format="cdr",
    )
    reader = rosbag2_py.SequentialReader()
    reader.open(storage_options, converter_options)
    return reader


def main():
    TABLE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Pass 1: count radar frames
    reader = open_reader()
    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    if RADAR_TOPIC not in type_map:
        raise RuntimeError(f"Missing topic in bag: {RADAR_TOPIC}")

    total_frames = 0
    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()
        if topic_name == RADAR_TOPIC:
            total_frames += 1

    if total_frames == 0:
        raise RuntimeError("No radar frames found.")

    selected_indices = choose_sample_indices(total_frames, MAX_ANALYSIS_FRAMES)
    selected_set = set(selected_indices)
    scatter_positions = choose_scatter_positions(len(selected_indices))

    print(f"Total radar frames in bag: {total_frames}")
    print(f"Sampled frames for analysis: {len(selected_indices)}")

    # Pass 2: process only selected frames
    reader = open_reader()
    msg_cls = get_message(type_map[RADAR_TOPIC])

    rows = []
    scatter_saved = []

    all_radial_velocity = []
    all_snr = []
    all_rcs = []
    point_counts = []

    frame_idx = -1
    sampled_pos = -1

    needed_fields = [
        "x",
        "y",
        "z",
        "radial_distance",
        "radial_velocity",
        "radar_cross_section",
        "signal_noise_ratio",
        "measurement_status",
    ]

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()
        if topic_name != RADAR_TOPIC:
            continue

        frame_idx += 1
        if frame_idx not in selected_set:
            continue

        sampled_pos += 1

        bag_time_s = bag_timestamp_ns / 1e9
        msg = deserialize_message(data, msg_cls)
        unified_time_s = get_unified_time(RADAR_TOPIC, msg, bag_time_s)
        time_source = get_time_source_label(RADAR_TOPIC, msg)

        field_names = [f.name for f in msg.fields]
        missing = [f for f in needed_fields if f not in field_names]
        if missing:
            raise RuntimeError(f"Missing expected radar fields: {missing}")

        pts = list(point_cloud2.read_points(msg, field_names=needed_fields, skip_nans=False))
        if len(pts) == 0:
            continue

        x = np.array([p[0] for p in pts], dtype=np.float32)
        y = np.array([p[1] for p in pts], dtype=np.float32)
        z = np.array([p[2] for p in pts], dtype=np.float32)
        radial_distance = np.array([p[3] for p in pts], dtype=np.float32)
        radial_velocity = np.array([p[4] for p in pts], dtype=np.float32)
        rcs = np.array([p[5] for p in pts], dtype=np.float32)
        snr = np.array([p[6] for p in pts], dtype=np.float32)
        measurement_status = np.array([p[7] for p in pts], dtype=np.float32)

        valid_xyz = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        valid_count = int(np.sum(valid_xyz))
        point_count = len(pts)
        point_counts.append(point_count)

        x_valid = x[valid_xyz]
        y_valid = y[valid_xyz]
        z_valid = z[valid_xyz]

        rv_valid = radial_velocity[np.isfinite(radial_velocity)]
        snr_valid = snr[np.isfinite(snr)]
        rcs_valid = rcs[np.isfinite(rcs)]

        if rv_valid.size > 0:
            all_radial_velocity.append(rv_valid)
        if snr_valid.size > 0:
            all_snr.append(snr_valid)
        if rcs_valid.size > 0:
            all_rcs.append(rcs_valid)

        rows.append({
            "frame_index_in_bag": frame_idx,
            "sampled_position": sampled_pos,
            "unified_time_s": unified_time_s,
            "time_source": time_source,
            "frame_id": msg.header.frame_id,
            "decoded_point_count": point_count,
            "valid_xyz_count": valid_count,
            "valid_ratio": valid_count / point_count if point_count else 0.0,
            "x_min": float(np.min(x_valid)) if valid_count else np.nan,
            "x_max": float(np.max(x_valid)) if valid_count else np.nan,
            "y_min": float(np.min(y_valid)) if valid_count else np.nan,
            "y_max": float(np.max(y_valid)) if valid_count else np.nan,
            "z_min": float(np.min(z_valid)) if valid_count else np.nan,
            "z_max": float(np.max(z_valid)) if valid_count else np.nan,
            "radial_distance_mean": float(np.mean(radial_distance[np.isfinite(radial_distance)])) if np.isfinite(radial_distance).any() else np.nan,
            "radial_velocity_mean": float(np.mean(rv_valid)) if rv_valid.size else np.nan,
            "radial_velocity_std": float(np.std(rv_valid)) if rv_valid.size else np.nan,
            "snr_mean": float(np.mean(snr_valid)) if snr_valid.size else np.nan,
            "rcs_mean": float(np.mean(rcs_valid)) if rcs_valid.size else np.nan,
            "measurement_status_unique": int(len(np.unique(measurement_status[np.isfinite(measurement_status)]))),
        })

        if sampled_pos in scatter_positions and valid_count > 0:
            plot_path = PLOTS_DIR / f"radar_xy_sample_{sampled_pos:02d}.png"
            save_xy_scatter(
                x_valid,
                y_valid,
                f"Radar XY scatter | sampled frame {sampled_pos} | raw idx {frame_idx}",
                plot_path,
            )
            scatter_saved.append(str(plot_path))

    df = pd.DataFrame(rows)
    df.to_csv(TABLE_OUTPUT, index=False)

    if all_radial_velocity:
        save_hist(np.concatenate(all_radial_velocity), "Radial velocity", "Radar sampled-frame radial velocity distribution", PLOTS_DIR / "radar_radial_velocity_hist.png")
    if all_snr:
        save_hist(np.concatenate(all_snr), "Signal-to-noise ratio", "Radar sampled-frame SNR distribution", PLOTS_DIR / "radar_snr_hist.png")
    if all_rcs:
        save_hist(np.concatenate(all_rcs), "Radar cross section", "Radar sampled-frame RCS distribution", PLOTS_DIR / "radar_rcs_hist.png")
    if point_counts:
        save_hist(np.array(point_counts), "Point count per sampled frame", "Radar sampled-frame point-count distribution", PLOTS_DIR / "radar_point_count_hist.png")

    print(f"Saved radar sampled content table to: {TABLE_OUTPUT}")
    print(f"Saved plots in: {PLOTS_DIR}")
    print(df.head().to_string(index=False))

    if scatter_saved:
        print("\nSaved XY scatter plots:")
        for p in scatter_saved:
            print(f"  {p}")


if __name__ == "__main__":
    main()