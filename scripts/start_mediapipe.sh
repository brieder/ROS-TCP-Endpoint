#!/bin/bash
ros2 launch mediapipe_ros2_py mp_node.launch.py model:=pose image_topic:=/cam_1/color/image_raw start_rviz:=true