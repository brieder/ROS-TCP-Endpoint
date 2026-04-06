#!/bin/bash
ros2 launch spinnaker_camera_driver driver_node.launch.py camera_type:=blackfly_s serial:="'23281048'"
ros2 run image_proc debayer_node --ros-args -r /image_raw:=/flir_camera/image_raw -r /image_color:=/camera_23281048/color/image_color
