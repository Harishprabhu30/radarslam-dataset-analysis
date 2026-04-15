from pathlib import Path
import pandas as pd


IMAGE_INPUT = Path("outputs/tables/camera_image_metadata.csv")
INFO_INPUT = Path("outputs/tables/camera_info_metadata.csv")
OUTPUT_SUMMARY = Path("outputs/tables/camera_timing_summary.txt")
OUTPUT_PAIRING = Path("outputs/tables/camera_stereo_pairing.csv")


def stats_block(series, name):
    s = series.dropna()
    if s.empty:
        return [f"{name}: no data"]
    return [
        f"{name}:",
        f"  count   = {len(s)}",
        f"  min     = {s.min():.6f}",
        f"  max     = {s.max():.6f}",
        f"  mean    = {s.mean():.6f}",
        f"  median  = {s.median():.6f}",
        f"  std     = {s.std():.6f}" if len(s) > 1 else "  std     = 0.000000",
    ]


def nearest_pairing(left_df, right_df):
    left_times = left_df["unified_time_s"].to_numpy()
    right_times = right_df["unified_time_s"].to_numpy()

    pairs = []
    j = 0

    for i, lt in enumerate(left_times):
        while j + 1 < len(right_times) and abs(right_times[j + 1] - lt) <= abs(right_times[j] - lt):
            j += 1

        rt = right_times[j]
        pairs.append({
            "left_index": i,
            "left_time_s": lt,
            "right_index": j,
            "right_time_s": rt,
            "abs_time_diff_s": abs(rt - lt),
        })

    return pd.DataFrame(pairs)


def main():
    if not IMAGE_INPUT.exists():
        raise FileNotFoundError(f"Missing file: {IMAGE_INPUT}")
    if not INFO_INPUT.exists():
        raise FileNotFoundError(f"Missing file: {INFO_INPUT}")

    df_img = pd.read_csv(IMAGE_INPUT).sort_values("unified_time_s").reset_index(drop=True)
    df_info = pd.read_csv(INFO_INPUT).sort_values("unified_time_s").reset_index(drop=True)

    left_img = df_img[df_img["topic"] == "/zed2i/zed_node/left/image_rect_color/compressed"].copy()
    right_img = df_img[df_img["topic"] == "/zed2i/zed_node/right/image_rect_color/compressed"].copy()
    left_info = df_info[df_info["topic"] == "/zed2i/zed_node/left/camera_info"].copy()
    right_info = df_info[df_info["topic"] == "/zed2i/zed_node/right/camera_info"].copy()

    for df in [left_img, right_img, left_info, right_info]:
        df["dt_s"] = df["unified_time_s"].diff()

    pairing_df = nearest_pairing(left_img, right_img)
    pairing_df.to_csv(OUTPUT_PAIRING, index=False)

    lines = []
    lines.append("Camera Timing and Stereo Consistency Summary")
    lines.append("=" * 60)
    lines.append("")

    lines.append("Image topic counts:")
    lines.append(f"  left images  = {len(left_img)}")
    lines.append(f"  right images = {len(right_img)}")
    lines.append("")

    lines.extend(stats_block(left_img["dt_s"], "left_image_dt_s"))
    lines.append("")
    lines.extend(stats_block(right_img["dt_s"], "right_image_dt_s"))
    lines.append("")

    lines.append("Camera info topic counts:")
    lines.append(f"  left camera_info  = {len(left_info)}")
    lines.append(f"  right camera_info = {len(right_info)}")
    lines.append("")

    lines.extend(stats_block(left_info["dt_s"], "left_camera_info_dt_s"))
    lines.append("")
    lines.extend(stats_block(right_info["dt_s"], "right_camera_info_dt_s"))
    lines.append("")

    lines.append("Stereo nearest-pair timing:")
    lines.extend(stats_block(pairing_df["abs_time_diff_s"], "left_to_right_abs_time_diff_s"))
    lines.append("")

    # Simple quality thresholds
    lines.append("Stereo pairing quality indicators:")
    lines.append(f"  pairs with abs_time_diff_s <= 0.005: {(pairing_df['abs_time_diff_s'] <= 0.005).sum()}")
    lines.append(f"  pairs with abs_time_diff_s <= 0.010: {(pairing_df['abs_time_diff_s'] <= 0.010).sum()}")
    lines.append(f"  pairs with abs_time_diff_s <= 0.020: {(pairing_df['abs_time_diff_s'] <= 0.020).sum()}")
    lines.append("")

    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved summary to: {OUTPUT_SUMMARY}")
    print(f"Saved stereo pairing table to: {OUTPUT_PAIRING}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()