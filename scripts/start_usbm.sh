#!/bin/bash
# Args: Serial /dev/videoX Width Height Framerate
ros2 run usb_cam usb_cam_node_exe --ros-args --remap __ns:=/camera_$1/color --params-file ./usb_cam_params_m.yaml -p video_device:=$2 -p image_width:=$3 -p image_height:=$4 -p framerate:=$5
