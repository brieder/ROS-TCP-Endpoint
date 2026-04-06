#!/bin/bash
source /opt/ros/humble/setup.bash
# original node name: image_republisher
ros2 run image_transport republish compressed raw --ros-args -r __node:=repub_$1 --remap in/compressed:=/$1/image_raw/compressed --remap out:=/$1/color/image_raw