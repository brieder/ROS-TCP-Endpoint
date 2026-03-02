#!/bin/bash
ros2 run realsense2_camera realsense2_camera_node --ros-args -p rgb_camera.color_profile:=960x540x60 -p enable_color:=true -p enable_depth:=false -p enable_infra1:=false -p enable_infra2:=false -r __node:=cam_1 -r __ns:=/
