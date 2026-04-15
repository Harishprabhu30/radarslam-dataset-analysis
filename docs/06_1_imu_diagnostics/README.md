# 06.1 IMU Diagnostics

## Goal
Evaluate IMU signal quality and compare multiple IMU sources.

## Metrics analysed
- sampling interval (dt)
- angular velocity statistics
- linear acceleration statistics
- acceleration magnitude
- gyro magnitude
- noise (std)
- bias (mean)

## Command

```bash
python3 -m scripts.06_1_imu_diagnostics
```

## Output Saved

`outputs/tables/imu_diagnostics_summary.txt`

## Initial IMU comparison conclusion

All three IMU topics appear physically plausible based on acceleration magnitude close to gravity.

### Strongest candidates
The most useful IMU topics for later analysis are:

1. `/zed2i/zed_node/imu/data`
2. `/imu/data`

Both use valid header timestamps and show reasonable acceleration magnitude near 9.81 m/s².

### Ouster IMU
`/ouster/imu` appears physically usable, but its timing is less reliable because it depends on bag-time alignment rather than valid message header timestamps. It should therefore be treated as a supporting IMU source rather than the primary reference IMU.

### Axis observations
The dominant gravity axis differs across sensors, indicating different sensor mounting orientations:
- `/imu/data`: gravity mainly on Y
- `/zed2i/zed_node/imu/data`: gravity mainly on negative Z
- `/ouster/imu`: gravity mainly on positive Z

### Working decision
For later motion analysis and possible fusion experiments, `/zed2i/zed_node/imu/data` and `/imu/data` should be prioritized.

## SELF LEARNING:

## 🧠 How to imagine the setup

Think of one machine carrying several sensor boxes.

For example:
main chassis
├── external IMU module
├── Ouster LiDAR (with its own built-in IMU)
└── ZED2i camera (with its own built-in IMU)


So there are multiple IMUs because each sensor often comes with its own internal IMU:

- **Ouster IMU** → inside the LiDAR unit  
- **ZED IMU** → inside the camera unit  
- `/imu/data` → likely an external dedicated IMU mounted on the robot body or sensor rig  

---

## 🧩 Key idea

This is very common in robotics:

> Different sensors = different clocks + different IMUs + different coordinate frames

So the system is not “one IMU”, but a **network of tightly mounted sensors**, each producing its own motion estimate and timestamps.

## 🌍 Why gravity axis differs

Gravity is always the same physical vector in the world.

But each IMU measures it in its own **local sensor frame**.

So if one IMU is rotated relative to another, gravity appears on different axes.

---

## 📌 Example
IMU A mounted upright → gravity mostly on +Z  
IMU B rotated sideways → gravity mostly on +Y  
IMU C upside down/tilted → gravity mostly on -Z  

So these can all be correct at the same time. That is likely what you are seeing:

/imu/data                  → gravity mainly on Y
/zed2i/zed_node/imu/data   → gravity mainly on -Z
/ouster/imu                → gravity mainly on +Z

This strongly suggests different sensor orientations, not necessarily bad data.

Should their values be almost similar?
Yes and no.
They should be similar in physics, but not identical in raw axes.

For the same machine:

These should be similar
- motion events happen at the same time
- turns should show up in gyro signals across all IMUs
- bumps/vibrations should appear across all IMUs
- gravity magnitude should be near 9.81 m/s²

These do NOT need to match directly
- raw ax, ay, az
- raw wx, wy, wz

because each IMU may have:

- different orientation
- different mounting location
- different noise
- different bias
- different filtering
- different vibration exposure

So raw values are usually not directly comparable axis-to-axis unless you rotate them into the same frame.

** Goto docs/06_2_imu_frame_alignment/README.md to know more on imu frame alignments details.