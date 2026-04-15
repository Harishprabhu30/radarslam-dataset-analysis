# 05.1 GNSS Diagnostics

## Goal
Evaluate whether the extracted GNSS trajectory is trustworthy enough to be used for later motion analysis.

## Why this stage matters
A GNSS topic may exist and still be unusable if it has:
- invalid fix status,
- unrealistic altitude,
- huge covariance,
- or physically impossible motion jumps.

## Input
`outputs/tables/gnss_trajectory.csv`

## Diagnostics performed
- status code distribution
- service code distribution
- GNSS time gap statistics
- point-to-point distance statistics
- implied speed statistics
- altitude statistics
- covariance statistics
- latitude/longitude bounds
- simple suspicion counters

## Command used

```bash
python3 -m scripts.05_1_gnss_diagnostics
```

## 📁 Outputs

`outputs/tables/gnss_diagnostics_summary.txt`
`outputs/tables/gnss_diagnostics_per_point.csv`

## Final conclusion

The GNSS data is not usable as a trajectory reference.

Evidence:
- All samples have `status_code = -1`, indicating no valid GNSS fix.
- Extremely large covariance values indicate high uncertainty.
- Altitude values (~10,000–12,000 m) are not physically consistent with the expected platform.
- Large position jumps result in unrealistic speeds (up to ~1.4 million km/h).
- Geographic bounds span hundreds of kilometers within a short time window.

Therefore:
- GNSS is rejected as a motion reference.
- GNSS may only be used for diagnostic purposes, not for trajectory evaluation or sensor fusion.

## Implication

All subsequent motion analysis must rely on:
- IMU
- LiDAR
- radar
- or visual sensors

GNSS will not be used as ground truth in this dataset.

