from pathlib import Path
import math
import pandas as pd

INPUT_PATH = Path("outputs/tables/gnss_trajectory.csv")
OUTPUT_SUMMARY_PATH = Path("outputs/tables/gnss_diagnostics_summary.txt")
OUTPUT_POINTS_PATH = Path("outputs/tables/gnss_diagnostics_per_point.csv")


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    required_cols = [
        "unified_time_s",
        "latitude_deg",
        "longitude_deg",
        "altitude_m",
        "status_code",
        "service_code",
        "cov_xx",
        "cov_yy",
        "cov_zz",
        "x_local_m",
        "y_local_m",
        "z_local_m",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df.sort_values("unified_time_s").reset_index(drop=True)

    # Consecutive deltas
    df["dt_s"] = df["unified_time_s"].diff()
    df["dx_m"] = df["x_local_m"].diff()
    df["dy_m"] = df["y_local_m"].diff()
    df["dz_m"] = df["z_local_m"].diff()

    df["step_distance_2d_m"] = (df["dx_m"]**2 + df["dy_m"]**2) ** 0.5
    df["step_distance_3d_m"] = (df["dx_m"]**2 + df["dy_m"]**2 + df["dz_m"]**2) ** 0.5

    df["speed_2d_mps"] = df["step_distance_2d_m"] / df["dt_s"]
    df["speed_3d_mps"] = df["step_distance_3d_m"] / df["dt_s"]
    df["speed_2d_kmph"] = df["speed_2d_mps"] * 3.6
    df["speed_3d_kmph"] = df["speed_3d_mps"] * 3.6

    # Status/service distributions
    status_counts = df["status_code"].value_counts(dropna=False).sort_index()
    service_counts = df["service_code"].value_counts(dropna=False).sort_index()

    # Basic stats helper
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
            f"  std     = {s.std():.6f}" if len(s) > 1 else f"  std     = 0.000000",
        ]

    lines = []
    lines.append("GNSS Diagnostics Summary")
    lines.append("=" * 60)
    lines.append(f"Input file: {INPUT_PATH}")
    lines.append(f"Total rows: {len(df)}")
    lines.append("")

    lines.append("Status code distribution:")
    for k, v in status_counts.items():
        lines.append(f"  {k}: {v}")
    lines.append("")

    lines.append("Service code distribution:")
    for k, v in service_counts.items():
        lines.append(f"  {k}: {v}")
    lines.append("")

    lines.extend(stats_block(df["dt_s"], "dt_s"))
    lines.append("")
    lines.extend(stats_block(df["step_distance_2d_m"], "step_distance_2d_m"))
    lines.append("")
    lines.extend(stats_block(df["speed_2d_mps"], "speed_2d_mps"))
    lines.append("")
    lines.extend(stats_block(df["speed_2d_kmph"], "speed_2d_kmph"))
    lines.append("")
    lines.extend(stats_block(df["altitude_m"], "altitude_m"))
    lines.append("")
    lines.extend(stats_block(df["cov_xx"], "cov_xx"))
    lines.append("")
    lines.extend(stats_block(df["cov_yy"], "cov_yy"))
    lines.append("")
    lines.extend(stats_block(df["cov_zz"], "cov_zz"))
    lines.append("")

    lines.append("Latitude/Longitude bounds:")
    lines.append(f"  lat_min = {df['latitude_deg'].min():.9f}")
    lines.append(f"  lat_max = {df['latitude_deg'].max():.9f}")
    lines.append(f"  lon_min = {df['longitude_deg'].min():.9f}")
    lines.append(f"  lon_max = {df['longitude_deg'].max():.9f}")
    lines.append("")

    # Simple suspicious thresholds
    suspicious_speed_count = (df["speed_2d_kmph"] > 200).sum(skipna=True)
    suspicious_altitude_count = ((df["altitude_m"] > 5000) | (df["altitude_m"] < -500)).sum()
    no_fix_count = (df["status_code"] == -1).sum()

    lines.append("Suspicion indicators:")
    lines.append(f"  rows with speed_2d_kmph > 200: {int(suspicious_speed_count)}")
    lines.append(f"  rows with altitude outside [-500, 5000] m: {int(suspicious_altitude_count)}")
    lines.append(f"  rows with status_code == -1: {int(no_fix_count)}")
    lines.append("")

    OUTPUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")
    df.to_csv(OUTPUT_POINTS_PATH, index=False)

    print(f"Saved summary to: {OUTPUT_SUMMARY_PATH}")
    print(f"Saved per-point diagnostics to: {OUTPUT_POINTS_PATH}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()