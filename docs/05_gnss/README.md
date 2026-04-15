# 05 GNSS Local Trajectory Extraction

## Goal
Extract GNSS messages from `/gnss` and convert them into a local trajectory for later motion analysis.

## Why this stage matters
GNSS provides the first directly usable global motion signal in the dataset.
To compare it with other sensors later, the data is converted into a local metric coordinate system.

## Time policy
GNSS uses header timestamps through the shared time alignment policy defined in Stage 4.2.

## Local frame definition
The first GNSS message is used as the local origin.

- `x_local_m` = east-west displacement in meters
- `y_local_m` = north-south displacement in meters
- `z_local_m` = altitude difference from the first fix

## Conversion method
A local tangent-plane approximation was used:

- `x = R * (lon - lon0) * cos(lat0)`
- `y = R * (lat - lat0)`
- `z = alt - alt0`

where:
- angles are converted to radians
- `R = 6378137.0 m`

## Command used

```bash
python3 scripts/05_extract_gnss.py
```

## Initial observations

Although GNSS extraction succeeded technically, the raw GNSS values appear unreliable for direct trajectory use.

Observed warning signs:
- `status_code = -1` for the extracted messages
- extremely large covariance values
- altitude around 11186 m
- large position jumps between consecutive samples

This suggests that the GNSS topic may represent:
- an invalid no-fix state,
- placeholder values,
- simulated or replayed coordinates,
- or otherwise unreliable positioning data.

Because of this, the extracted GNSS trajectory should currently be treated as a raw diagnostic output, not a trusted reference trajectory.