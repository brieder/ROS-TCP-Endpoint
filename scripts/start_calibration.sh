#!/bin/bash

# $1 - camera name

source /opt/ros/humble/setup.bash
echo $$ > /workspaces/vdt/scripts/calibration.pid

#exec ros2 launch vdt calibration.launch.py camera_name:=$1
ros2 run camera_calibration cameracalibrator --size 6x4 --square 0.030 --ros-args --remap camera:=/$1 --remap image:=/$1/color/image_raw