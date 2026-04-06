#!/bin/bash
ros2 run realsense2_camera realsense2_camera_node --ros-args -p rgb_camera.color_profile:=640x480x30 -p enable_color:=true -p enable_depth:=false -p enable_infra1:=false -p enable_infra2:=false -p enable_gyro:=false -p enable_accel:=false -p serial_no:=$1 -r __node:=camera$1 -r __ns:=/
