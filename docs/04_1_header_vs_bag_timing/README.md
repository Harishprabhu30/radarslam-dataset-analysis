# 04.1 Header Timestamp vs Bag Timestamp

## Goal
Compare bag record timestamps with message header timestamps for major sensor topics.

## Why this stage matters
Bag record time describes when messages were written into the bag.
Header timestamp describes when the message claims the data was acquired or stamped by the source node.

A difference between the two can reveal:
- recorder-side burst writing,
- transport delays,
- batching effects,
- driver timestamp behavior.

## Topics analysed
- /gnss
- /imu/data
- /off_highway_premium_radar_sample_driver/locations
- /ouster/imu
- /ouster/points
- /ouster/scan
- /zed2i/zed_node/imu/data
- /zed2i/zed_node/left/image_rect_color/compressed
- /zed2i/zed_node/right/image_rect_color/compressed

## Command used

```bash
python3 scripts/04_1_header_vs_bag_timing.py
```

## Output

`outputs/tables/topic_header_vs_bag_timing.csv`

## Key Findings

## Record dates are different
Header time → July 2025
Bag time    → Feb 2026

### 1. Different time domains

A constant offset of approximately 1.85e7 seconds was observed between bag timestamps and header timestamps.

This indicates that:
- header timestamps originate from a different clock (likely original acquisition time)
- bag timestamps correspond to recording or replay time

### 2. Sensor timing behavior

For most sensors:

- header timestamps show consistent and physically meaningful sampling rates
- bag timestamps show burst-like behavior and are not suitable for fine timing analysis

### 3. Ouster anomaly

For Ouster topics:
- header timestamps are invalid or inconsistent
- negative durations and incorrect intervals are observed

Therefore:
- header timestamps for Ouster data are not reliable
- bag timestamps should be used for Ouster timing

### 4. Interpretation

This dataset appears to have been:
- recorded or replayed after original acquisition
- stored with original sensor timestamps preserved in headers

This creates a dual-clock scenario which must be handled carefully in analysis.

## NOTE TO ME: Always ensure, NOT to treat bag timestamp as ground truth timing. USE header timestamp when available and valid and EXCEPT for Ouster → use bag time

# What likely happened?

## From your findings

Header time → July 2025  
Bag time → Feb 2026  

So the most likely pipeline is:

```text
[Original data acquisition]
    ↓
Sensors recorded with proper timestamps (header.stamp)
    ↓
Saved / logged / stored somewhere
    ↓
Later replayed (Feb 2026)
    ↓
ros2 bag record was run during replay

So your bag is:

- **NOT** a direct live recording  
- **BUT** a replay-based recording  

---

## Simple mental model

Think of it like:

```text
Original event → video shot in July
Your bag       → screen recording of that video in Feb

- The video timestamp (`header`) is original truth.  
- The screen recording time (`bag`) is when it was replayed.  

## ⚙️ Is this a bad way to record data?

❌ Not “bad” — but context-dependent  

### ✔ GOOD for:
- Dataset sharing  
- Offline analysis  
- SLAM evaluation (if header timestamps are used)  
- Reproducibility  
- Benchmarking  

### ❌ BAD for:
- Real-time system evaluation  
- Latency measurement  
- Sensor synchronization debugging  
- Control loop validation  
- Hardware timing validation  

## 🔥 The real problem is NOT replay — it’s misuse

The danger is:

If someone uses **bag timestamps** instead of **header timestamps** → **WRONG conclusions**

### Example:

You already saw:

- IMU appears bursty → ❌ (bag timestamp illusion)  
- IMU is actually stable → ✅ (header timestamp truth)  

---

## ⚠️ Where instability can happen

### 1. If you use wrong timestamps

Using **bag time** instead of **header time**  
→ incorrect `dt`  
→ wrong velocity / integration  
→ unstable EKF / SLAM  

---

### 2. If replay was not done properly

Bad replay setup can cause:

- message bursts  
- queue overflow  
- TF delays  
- dropped messages  

But your dataset seems:

**Header timing = clean**  
→ replay preserved original timing information  

---

### 3. Sensor-specific issue (Ouster)

This is the only real problem in your dataset:

### Ouster header timestamps are broken

So:

LiDAR timing = must rely on **bag timestamps**

That is a limitation.

---

## 📊 Final judgment of your dataset

**Overall quality:**  
**GOOD dataset (with one caveat)**

### ✔ Strengths
- Multi-sensor rich (LiDAR + IMU + GNSS + camera + radar)  
- Header timestamps preserved  
- GNSS, IMU, camera are clean  
- Suitable for offline SLAM / analysis  

### ⚠️ Weakness
- Ouster header timestamps unreliable  
- Dual time domains (needs careful handling)  

---

## 🧠 What you should assume going forward

Use this rule:

```text
For analysis:
    use header timestamps (truth)

For Ouster:
    use bag timestamps (fallback)

## ❓ Will this cause instability in SLAM / fusion?

### ✔ If handled correctly → NO

If you:

- ✔ use header timestamps for IMU / GNSS / camera  
- ✔ use consistent time base  
- ✔ align sensors properly  

Then:

→ stable results possible  

---

### ✖ If handled incorrectly → YES

If you:

- ✖ mix bag time and header time blindly  
- ✖ compute `dt` from bag time  
- ✖ ignore offsets  

Then:

→ drift  
→ inconsistent motion  
→ EKF divergence  
→ bad trajectory  


## My View:

I would define a time policy for this dataset:

## 🕒 Time Policy

**Primary time source:**
    header.stamp (IMU, GNSS, camera, radar)

**Fallback:**
    bag timestamp (Ouster only)

**Rule:**
    Never mix both without explicit alignment.

** Goto docs/04_2_time_alignment.md to know more.