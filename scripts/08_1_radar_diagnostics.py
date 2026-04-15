from pathlib import Path
import pandas as pd

INPUT_PATH = Path("outputs/tables/radar_metadata.csv")
OUTPUT_SUMMARY = Path("outputs/tables/radar_diagnostics_summary.txt")


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

    df = pd.read_csv(INPUT_PATH).sort_values("unified_time_s").reset_index(drop=True)
    df["dt_s"] = df["unified_time_s"].diff()

    lines = []
    lines.append("Radar Diagnostics Summary")
    lines.append("=" * 60)
    lines.append(f"Input file: {INPUT_PATH}")
    lines.append(f"Total frames: {len(df)}")
    lines.append("")

    lines.append(f"Unique frame_id values: {df['frame_id'].nunique()}")
    lines.append(f"Unique field_names values: {df['field_names'].nunique()}")
    lines.append(f"Unique field_count values: {df['field_count'].nunique()}")
    lines.append(f"Unique point_step values: {df['point_step'].nunique()}")
    lines.append(f"Unique is_dense values: {df['is_dense'].nunique()}")
    lines.append("")

    lines.extend(stats_block(df["dt_s"], "radar_dt_s"))
    lines.append("")
    lines.extend(stats_block(df["estimated_point_count"], "estimated_point_count"))
    lines.append("")
    lines.extend(stats_block(df["data_length_bytes"], "data_length_bytes"))
    lines.append("")

    OUTPUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    print(f"Saved radar diagnostics summary to: {OUTPUT_SUMMARY}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()