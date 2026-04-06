#!/bin/bash
source /opt/ros/humble/setup.bash
echo $$ > /workspaces/vdt/scripts/apriltag_$1.pid
ros2 run apriltag_ros apriltag_node --ros-args -r __node:=apriltags_$1  -r image_rect:=/$1/color/image_raw -r camera_info:=/$1/color/camera_info -r detections:=apriltag_detections --params-file /workspaces/vdt/configs/apriltags_36h11.yaml