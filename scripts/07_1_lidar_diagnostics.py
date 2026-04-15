from pathlib import Path
import pandas as pd

POINTS_INPUT = Path("outputs/tables/ouster_points_metadata.csv")
SCAN_INPUT = Path("outputs/tables/ouster_scan_metadata.csv")
OUTPUT_SUMMARY = Path("outputs/tables/lidar_diagnostics_summary.txt")


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


def main():
    if not POINTS_INPUT.exists():
        raise FileNotFoundError(f"Missing file: {POINTS_INPUT}")
    if not SCAN_INPUT.exists():
        raise FileNotFoundError(f"Missing file: {SCAN_INPUT}")

    df_points = pd.read_csv(POINTS_INPUT).sort_values("unified_time_s").reset_index(drop=True)
    df_scan = pd.read_csv(SCAN_INPUT).sort_values("unified_time_s").reset_index(drop=True)

    df_points["dt_s"] = df_points["unified_time_s"].diff()
    df_scan["dt_s"] = df_scan["unified_time_s"].diff()

    lines = []
    lines.append("LiDAR Diagnostics Summary")
    lines.append("=" * 60)
    lines.append("")

    lines.append("/ouster/points")
    lines.append("-" * 40)
    lines.append(f"Total frames: {len(df_points)}")
    lines.append(f"Unique frame_id values: {df_points['frame_id'].nunique()}")
    lines.append(f"Unique field_names values: {df_points['field_names'].nunique()}")
    lines.append(f"Unique estimated_point_count values: {df_points['estimated_point_count'].nunique()}")
    lines.append(f"Unique point_step values: {df_points['point_step'].nunique()}")
    lines.append(f"Unique row_step values: {df_points['row_step'].nunique()}")
    lines.append(f"Unique data_length_bytes values: {df_points['data_length_bytes'].nunique()}")
    lines.append(f"Unique is_dense values: {df_points['is_dense'].nunique()}")
    lines.append("")

    lines.extend(stats_block(df_points["dt_s"], "points_dt_s"))
    lines.append("")
    lines.extend(stats_block(df_points["estimated_point_count"], "estimated_point_count"))
    lines.append("")
    lines.extend(stats_block(df_points["data_length_bytes"], "data_length_bytes"))
    lines.append("")

    lines.append("/ouster/scan")
    lines.append("-" * 40)
    lines.append(f"Total frames: {len(df_scan)}")
    lines.append(f"Unique frame_id values: {df_scan['frame_id'].nunique()}")
    lines.append(f"Unique ranges_count values: {df_scan['ranges_count'].nunique()}")
    lines.append(f"Unique intensities_count values: {df_scan['intensities_count'].nunique()}")
    lines.append(f"Unique scan_time values: {df_scan['scan_time'].nunique()}")
    lines.append(f"Unique range_min values: {df_scan['range_min'].nunique()}")
    lines.append(f"Unique range_max values: {df_scan['range_max'].nunique()}")
    lines.append("")
    lines.extend(stats_block(df_scan["dt_s"], "scan_dt_s"))
    lines.append("")
    lines.extend(stats_block(df_scan["ranges_count"], "ranges_count"))
    lines.append("")
    lines.extend(stats_block(df_scan["scan_time"], "scan_time"))
    lines.append("")

    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved LiDAR diagnostics summary to: {OUTPUT_SUMMARY}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()