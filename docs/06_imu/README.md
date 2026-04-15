# 06 IMU Extraction

## Goal
Extract all major IMU topics into a unified analysis table for later comparison and quality inspection.

## IMU topics included
- /imu/data
- /ouster/imu
- /zed2i/zed_node/imu/data

## Time policy
The shared dataset time policy from Stage 4.2 is used:
- valid header timestamps are used directly
- Ouster IMU uses bag time converted into the master time domain

## Output fields
The extraction stores:
- unified time
- time source label
- bag time
- frame id
- orientation quaternion
- angular velocity
- linear acceleration
- selected covariance diagonal terms

## Command used

```bash
python3 -m scripts.06_extract_imu
```

## Output Saved:

`outputs/tables/imu_all.csv`

## 📊 Stage 6 Extraction Interpretation

Everything is consistent:

- `/imu/data` → header ✅  
- `/zed2i/zed_node/imu/data` → header ✅  
- `/ouster/imu` → bag_minus_offset ✅  

---

### 📈 Counts also match earlier expectations:

39312 + 26432 + 13600 = 79344


---

## 🧠 Conclusion

- Time policy is working correctly  
- Extraction is correct  
- Dataset is consistent  

** Next goto docs/06_1_imu_diagnostics/README.md for more imu detail
