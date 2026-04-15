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
POINTS_TOPIC = "/ouster/points"

TABLE_OUTPUT = Path("outputs/tables/ouster_points_content_sampled.csv")
PLOTS_DIR = Path("outputs/plots")

MAX_ANALYSIS_FRAMES = 20
SCATTER_FRAME_COUNT = 3
XY_SCATTER_MAX_POINTS = 8000
HIST_SAMPLE_PER_FRAME = 3000


def finite_mask(*arrays):
    mask = np.ones(len(arrays[0]), dtype=bool)
    for arr in arrays:
        mask &= np.isfinite(arr)
    return mask


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
    plt.hist(data, bins=60)
    plt.xlabel(xlabel)
    plt.ylabel("Count")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_xy_scatter(x, y, title, path):
    plt.figure(figsize=(7, 7))
    plt.scatter(x, y, s=0.5)
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

    # Pass 1: count frames
    reader = open_reader()
    topic_types = reader.get_all_topics_and_types()
    type_map = {topic.name: topic.type for topic in topic_types}

    if POINTS_TOPIC not in type_map:
        raise RuntimeError(f"Missing topic in bag: {POINTS_TOPIC}")

    total_frames = 0
    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()
        if topic_name == POINTS_TOPIC:
            total_frames += 1

    if total_frames == 0:
        raise RuntimeError("No /ouster/points frames found.")

    selected_indices = choose_sample_indices(total_frames, MAX_ANALYSIS_FRAMES)
    selected_set = set(selected_indices)
    scatter_positions = choose_scatter_positions(len(selected_indices))

    print(f"Total /ouster/points frames in bag: {total_frames}")
    print(f"Sampled frames for analysis: {len(selected_indices)}")

    # Pass 2: process only selected frames
    reader = open_reader()
    msg_cls = get_message(type_map[POINTS_TOPIC])

    rows = []
    hist_ranges = []
    hist_intensity = []
    hist_reflectivity = []
    scatter_saved = []

    frame_idx = -1
    sampled_pos = -1

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()
        if topic_name != POINTS_TOPIC:
            continue

        frame_idx += 1
        if frame_idx not in selected_set:
            continue

        sampled_pos += 1

        bag_time_s = bag_timestamp_ns / 1e9
        msg = deserialize_message(data, msg_cls)

        unified_time_s = get_unified_time(POINTS_TOPIC, msg, bag_time_s)
        time_source = get_time_source_label(POINTS_TOPIC, msg)  # ✅ FIXED LINE

        needed_fields = ["x", "y", "z", "intensity", "reflectivity", "ambient", "range", "ring"]
        points_iter = point_cloud2.read_points(
            msg,
            field_names=needed_fields,
            skip_nans=False,
        )

        points = list(points_iter)

        if len(points) == 0:
            continue

        x = np.array([p[0] for p in points], dtype=np.float32)
        y = np.array([p[1] for p in points], dtype=np.float32)
        z = np.array([p[2] for p in points], dtype=np.float32)
        intensity = np.array([p[3] for p in points], dtype=np.float32)
        reflectivity = np.array([p[4] for p in points], dtype=np.float32)
        ambient = np.array([p[5] for p in points], dtype=np.float32)
        range_field = np.array([p[6] for p in points], dtype=np.float32)
        ring = np.array([p[7] for p in points], dtype=np.float32)

        xyz_valid = finite_mask(x, y, z)
        valid_xyz_count = int(np.sum(xyz_valid))
        decoded_point_count = len(points)
        invalid_xyz_count = decoded_point_count - valid_xyz_count
        valid_ratio = valid_xyz_count / decoded_point_count if decoded_point_count else 0.0

        x_valid = x[xyz_valid]
        y_valid = y[xyz_valid]
        z_valid = z[xyz_valid]
        intensity_valid = intensity[xyz_valid]
        reflectivity_valid = reflectivity[xyz_valid]
        ambient_valid = ambient[xyz_valid]
        range_valid = range_field[xyz_valid]
        ring_valid = ring[xyz_valid]

        rows.append({
            "frame_index_in_bag": frame_idx,
            "sampled_position": sampled_pos,
            "unified_time_s": unified_time_s,
            "time_source": time_source,
            "frame_id": msg.header.frame_id,
            "height": msg.height,
            "width": msg.width,
            "estimated_point_count": msg.width * msg.height,
            "decoded_point_count": decoded_point_count,
            "valid_xyz_count": valid_xyz_count,
            "invalid_xyz_count": invalid_xyz_count,
            "valid_ratio": valid_ratio,
            "x_min": float(np.min(x_valid)) if valid_xyz_count else np.nan,
            "x_max": float(np.max(x_valid)) if valid_xyz_count else np.nan,
            "y_min": float(np.min(y_valid)) if valid_xyz_count else np.nan,
            "y_max": float(np.max(y_valid)) if valid_xyz_count else np.nan,
            "z_min": float(np.min(z_valid)) if valid_xyz_count else np.nan,
            "z_max": float(np.max(z_valid)) if valid_xyz_count else np.nan,
            "range_min": float(np.min(range_valid[np.isfinite(range_valid)])) if np.isfinite(range_valid).any() else np.nan,
            "range_max": float(np.max(range_valid[np.isfinite(range_valid)])) if np.isfinite(range_valid).any() else np.nan,
            "range_mean": float(np.mean(range_valid[np.isfinite(range_valid)])) if np.isfinite(range_valid).any() else np.nan,
            "intensity_mean": float(np.mean(intensity_valid[np.isfinite(intensity_valid)])) if np.isfinite(intensity_valid).any() else np.nan,
            "reflectivity_mean": float(np.mean(reflectivity_valid[np.isfinite(reflectivity_valid)])) if np.isfinite(reflectivity_valid).any() else np.nan,
            "ambient_mean": float(np.mean(ambient_valid[np.isfinite(ambient_valid)])) if np.isfinite(ambient_valid).any() else np.nan,
            "unique_ring_count": int(len(np.unique(ring_valid[np.isfinite(ring_valid)]))) if valid_xyz_count else 0,
        })

        finite_range = range_valid[np.isfinite(range_valid)]
        finite_intensity = intensity_valid[np.isfinite(intensity_valid)]
        finite_reflectivity = reflectivity_valid[np.isfinite(reflectivity_valid)]

        for src, dst in [
            (finite_range, hist_ranges),
            (finite_intensity, hist_intensity),
            (finite_reflectivity, hist_reflectivity),
        ]:
            if src.size > 0:
                if src.size > HIST_SAMPLE_PER_FRAME:
                    idx = np.linspace(0, src.size - 1, HIST_SAMPLE_PER_FRAME, dtype=int)
                    dst.append(src[idx])
                else:
                    dst.append(src)

        if sampled_pos in scatter_positions and valid_xyz_count > 0:
            if valid_xyz_count > XY_SCATTER_MAX_POINTS:
                idx = np.linspace(0, valid_xyz_count - 1, XY_SCATTER_MAX_POINTS, dtype=int)
                xs = x_valid[idx]
                ys = y_valid[idx]
            else:
                xs = x_valid
                ys = y_valid

            plot_path = PLOTS_DIR / f"ouster_points_xy_sample_{sampled_pos:02d}.png"
            save_xy_scatter(xs, ys, f"Ouster XY scatter | sampled frame {sampled_pos} | raw idx {frame_idx}", plot_path)
            scatter_saved.append(str(plot_path))

    df = pd.DataFrame(rows)
    df.to_csv(TABLE_OUTPUT, index=False)

    if hist_ranges:
        save_hist(np.concatenate(hist_ranges), "Range", "Ouster sampled-frame range distribution", PLOTS_DIR / "ouster_range_hist.png")
    if hist_intensity:
        save_hist(np.concatenate(hist_intensity), "Intensity", "Ouster sampled-frame intensity distribution", PLOTS_DIR / "ouster_intensity_hist.png")
    if hist_reflectivity:
        save_hist(np.concatenate(hist_reflectivity), "Reflectivity", "Ouster sampled-frame reflectivity distribution", PLOTS_DIR / "ouster_reflectivity_hist.png")

    print(f"Saved sampled content table to: {TABLE_OUTPUT}")
    print(f"Saved plots in: {PLOTS_DIR}")


if __name__ == "__main__":
    main()