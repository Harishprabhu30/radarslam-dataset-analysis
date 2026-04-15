from pathlib import Path
import math
import pandas as pd

import rosbag2_py
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from scripts.time_utils import get_unified_time, get_time_source_label


BAG_PATH = "/workspace/raw/data/rosbag_2025_07_17-15-11-39_lidar_imu_bosch_comp-zed-os-pcd_0.mcap"
TOPIC_NAME = "/gnss"
OUTPUT_PATH = Path("outputs/tables/gnss_trajectory.csv")

EARTH_RADIUS_M = 6378137.0


def latlon_to_local_xy(lat_deg, lon_deg, lat0_deg, lon0_deg):
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    lat0 = math.radians(lat0_deg)
    lon0 = math.radians(lon0_deg)

    x_local = EARTH_RADIUS_M * (lon - lon0) * math.cos(lat0)
    y_local = EARTH_RADIUS_M * (lat - lat0)

    return x_local, y_local


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

    if TOPIC_NAME not in type_map:
        raise RuntimeError(f"Topic not found in bag: {TOPIC_NAME}")

    msg_type = get_message(type_map[TOPIC_NAME])

    rows = []

    lat0 = None
    lon0 = None
    alt0 = None

    while reader.has_next():
        topic_name, data, bag_timestamp_ns = reader.read_next()

        if topic_name != TOPIC_NAME:
            continue

        msg = deserialize_message(data, msg_type)
        bag_time_s = bag_timestamp_ns / 1e9

        unified_time_s = get_unified_time(topic_name, msg, bag_time_s)
        time_source = get_time_source_label(topic_name, msg)

        latitude = msg.latitude
        longitude = msg.longitude
        altitude = msg.altitude
        frame_id = msg.header.frame_id

        status_code = msg.status.status
        service_code = msg.status.service

        covariance = list(msg.position_covariance)
        covariance_type = msg.position_covariance_type

        # Use first GNSS message as local origin
        if lat0 is None:
            lat0 = latitude
            lon0 = longitude
            alt0 = altitude

        x_local_m, y_local_m = latlon_to_local_xy(latitude, longitude, lat0, lon0)
        z_local_m = altitude - alt0

        rows.append({
            "unified_time_s": unified_time_s,
            "time_source": time_source,
            "frame_id": frame_id,
            "latitude_deg": latitude,
            "longitude_deg": longitude,
            "altitude_m": altitude,
            "status_code": status_code,
            "service_code": service_code,
            "cov_xx": covariance[0],
            "cov_xy": covariance[1],
            "cov_xz": covariance[2],
            "cov_yx": covariance[3],
            "cov_yy": covariance[4],
            "cov_yz": covariance[5],
            "cov_zx": covariance[6],
            "cov_zy": covariance[7],
            "cov_zz": covariance[8],
            "covariance_type": covariance_type,
            "x_local_m": x_local_m,
            "y_local_m": y_local_m,
            "z_local_m": z_local_m,
        })

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("No GNSS messages were extracted.")

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved GNSS trajectory to: {OUTPUT_PATH}")
    print(f"Extracted {len(df)} GNSS messages")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    main()