from pathlib import Path
import numpy as np
import pandas as pd

INPUT_PATH = Path("outputs/tables/imu_all.csv")
OUTPUT_SUMMARY_PATH = Path("outputs/tables/imu_diagnostics_summary.txt")


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
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing file: {INPUT_PATH}")

    df = pd.read_csv(INPUT_PATH)

    lines = []
    lines.append("IMU Diagnostics Summary")
    lines.append("=" * 60)

    for imu_topic, group in df.groupby("imu_topic"):
        group = group.sort_values("unified_time_s").reset_index(drop=True)

        lines.append("")
        lines.append(f"IMU Topic: {imu_topic}")
        lines.append("-" * 40)

        # Timing
        dt = group["unified_time_s"].diff()

        lines.extend(stats_block(dt, "dt_s"))
        lines.append("")

        # Angular velocity
        wx = group["angular_velocity_x"]
        wy = group["angular_velocity_y"]
        wz = group["angular_velocity_z"]

        gyro_mag = np.sqrt(wx**2 + wy**2 + wz**2)

        lines.extend(stats_block(wx, "angular_velocity_x"))
        lines.extend(stats_block(wy, "angular_velocity_y"))
        lines.extend(stats_block(wz, "angular_velocity_z"))
        lines.extend(stats_block(gyro_mag, "gyro_magnitude"))
        lines.append("")

        # Linear acceleration
        ax = group["linear_acceleration_x"]
        ay = group["linear_acceleration_y"]
        az = group["linear_acceleration_z"]

        acc_mag = np.sqrt(ax**2 + ay**2 + az**2)

        lines.extend(stats_block(ax, "linear_acceleration_x"))
        lines.extend(stats_block(ay, "linear_acceleration_y"))
        lines.extend(stats_block(az, "linear_acceleration_z"))
        lines.extend(stats_block(acc_mag, "acc_magnitude"))
        lines.append("")

        # Quick checks
        mean_acc_mag = acc_mag.mean()
        std_acc_mag = acc_mag.std()

        lines.append("Quick checks:")
        lines.append(f"  mean(acc_magnitude) ≈ {mean_acc_mag:.3f} m/s²")
        lines.append(f"  std(acc_magnitude)  ≈ {std_acc_mag:.3f}")
        lines.append("")

    OUTPUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved IMU diagnostics to: {OUTPUT_SUMMARY_PATH}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

    