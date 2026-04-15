# 03 TF Tree and Frame Inspection

## Goal
Inspect the coordinate frames used by the dataset and check whether the main sensors are connected through TF.

## Commands Used

```bash
ros2 run tf2_tools view_frames
ros2 topic echo /ouster/points --once | grep frame_id
ros2 topic echo /ouster/imu --once | grep frame_id
ros2 topic echo /imu/data --once | grep frame_id
ros2 topic echo /gnss --once | grep frame_id
ros2 topic echo /off_highway_premium_radar_sample_driver/locations --once | grep frame_id
ros2 topic echo /zed2i/zed_node/left/image_rect_color/compressed --once | grep frame_id

## Observed Frame IDs

| Topic | frame_id |
|------|----------|
| /ouster/points | os_lidar |
| /ouster/imu | os_imu |
| /imu/data | sensor_box/imu_link |
| /gnss | sensor_box/imu_link |
| /off_highway_premium_radar_sample_driver/locations | base_link |
| /zed2i/zed_node/left/image_rect_color/compressed | zed2i_left_camera_optical_frame |

---

## TF Graph Findings

The generated TF graph clearly shows the ZED2i camera chain:

- zed2i_base_link  
- zed2i_camera_center  
- zed2i_left_camera_frame  
- zed2i_left_camera_optical_frame  
- zed2i_right_camera_frame  
- zed2i_right_camera_optical_frame  
- zed2i_imu_link  

It also shows a dynamic transform related to:

- imu_link/world  
  - parent: sensor_box/imu_link  

---

## Important Observation

Some topic `frame_id`s observed from the messages were not clearly visible in the TF graph snippet, including:

- os_lidar  
- os_imu  
- base_link  

This means one of the following may be true:

- those transforms are missing from the recorded TF tree  
- they were not captured clearly in the short `view_frames` snapshot  
- the frame exists in messages but is not fully connected in TF  
- the graph snippet shown in terminal is only partial  

---

## Conclusion

The dataset definitely contains multiple frame namespaces:

- Ouster frames  
- ZED2i frames  
- sensor_box IMU frame  
- base_link  

The ZED2i chain is clearly visible.

The full connectivity between LiDAR, radar, IMU, GNSS, and base frames still needs deeper TF checking if later fusion depends on exact transforms.


## What matters from this stage

Two important technical points:

```text id="nh8l7x"
1. GNSS and external IMU both use sensor_box/imu_link.
2. Radar uses base_link, while Ouster uses os_lidar / os_imu.

That already tells you the dataset may have multiple frame families, and later analysis must respect that.

## Next Stage

Now moving to:

## Stage 4: Timing and Rate Quality Analysis

- what topics exist  
- what frames they claim  
- and you can begin checking how regularly they were recorded  