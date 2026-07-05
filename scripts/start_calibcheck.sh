#!/bin/bash

# $1 - camera name
# $2 - chessboard size (inner corners)
# $3 - chessboard square size in meters

source /opt/ros/$ROS_DISTRO/setup.bash

echo $$ > /workspaces/vdt/scripts/calibration.pid

#ros2 run camera_calibration cameracheck --size ${2:-8x6} --ros-args --remap /monocular/image_rect:=/C$1/color/image_color --remap image:=/C$1/color/image_color
ros2 run camera_calibration cameracheck --size ${2:-9x7} --square ${3:-0.075} --ros-args --remap /monocular/image_rect:=/C$1/color/image_raw --remap /monocular/camera_info:=/C$1/color/camera_info
