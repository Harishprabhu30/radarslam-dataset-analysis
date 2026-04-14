from pathlib import Path
import yaml
import pandas as pd

DURATION_SECONDS = 269.341840121

METADATA_PATH = Path("data/metadata/original_metadata.yaml")
OUTPUT_PATH = Path("outputs/tables/topic_summary.csv")

def guess_sensor_group(topic: str) -> str:
    if topic.startswith("/ouster"):
        return "Ouster LiDAR / Ouster IMU"
    if topic.startswith("/zed2i"):
        return "ZED2i Camera / ZED2i IMU"
    if topic.startswith("/imu"):
        return "External IMU"
    if topic.startswith("/gnss"):
        return "GNSS"
    if "radar" in topic:
        return "Radar"
    if topic in ["/tf", "/tf_static"]:
        return "TF"
    if topic in ["/clock"]:
        return "Clock"
    return "System / Other"

def guess_priority(count: int, topic: str) -> str:
    if count == 0:
        return "Low"
    if topic in [
        "/ouster/points",
        "/ouster/imu",
        "/imu/data",
        "/gnss",
        "/tf",
        "/tf_static",
        "/off_highway_premium_radar_sample_driver/locations",
    ]:
        return "High"
    if topic.startswith("/zed2i/zed_node") or topic.startswith("/ouster"):
        return "Medium"
    return "Low"

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(METADATA_PATH, "r") as f:
        metadata = yaml.safe_load(f)

    topics = metadata["rosbag2_bagfile_information"]["topics_with_message_count"]

    rows = []

    for item in topics:
        topic_meta = item["topic_metadata"]
        topic = topic_meta["name"]
        msg_type = topic_meta["type"]
        count = item["message_count"]
        hz = count / DURATION_SECONDS if DURATION_SECONDS > 0 else 0.0

        rows.append({
            "topic": topic,
            "type": msg_type,
            "count": count,
            "approx_hz": round(hz, 3),
            "sensor_group": guess_sensor_group(topic),
            "priority": guess_priority(count, topic),
        })

    df = pd.DataFrame(rows)
    df = df.sort_values(by=["priority", "sensor_group", "topic"])

    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved topic summary to: {OUTPUT_PATH}")
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()