from typing import Optional

TIME_OFFSET_S = 18582410.0

HEADER_TOPICS = {
    "/gnss",
    "/imu/data",
    "/off_highway_premium_radar_sample_driver/locations",
    "/zed2i/zed_node/imu/data",
    "/zed2i/zed_node/left/image_rect_color/compressed",
    "/zed2i/zed_node/right/image_rect_color/compressed",
}

OUSTER_BAG_TOPICS = {
    "/ouster/imu",
    "/ouster/points",
    "/ouster/scan",
}


def stamp_to_sec(stamp) -> float:
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


def has_valid_header_stamp(msg) -> bool:
    if not hasattr(msg, "header"):
        return False
    if not hasattr(msg.header, "stamp"):
        return False
    stamp = msg.header.stamp
    t = stamp_to_sec(stamp)
    return t > 0.0


# =========================================================
# ORIGINAL FUNCTION (UNCHANGED)
# =========================================================
def get_unified_time(topic_name: str, msg, bag_time_s: float) -> Optional[float]:
    """
    Return unified time in the chosen dataset master time domain.
    """
    if topic_name in HEADER_TOPICS and has_valid_header_stamp(msg):
        return stamp_to_sec(msg.header.stamp)

    if topic_name in OUSTER_BAG_TOPICS:
        return bag_time_s - TIME_OFFSET_S

    if has_valid_header_stamp(msg):
        return stamp_to_sec(msg.header.stamp)

    return bag_time_s


# =========================================================
# NEW: LABEL FUNCTION (DOES NOT MODIFY ORIGINAL LOGIC)
# =========================================================
def get_time_source_label(topic_name: str, msg, bag_time_s: float) -> str:
    """
    Returns which time source would be used by get_unified_time().
    Purely diagnostic / annotation function.
    """

    if topic_name in HEADER_TOPICS and has_valid_header_stamp(msg):
        return "header"

    if topic_name in OUSTER_BAG_TOPICS:
        return "bag_minus_offset"

    if has_valid_header_stamp(msg):
        return "header_fallback"

    return "bag_fallback"