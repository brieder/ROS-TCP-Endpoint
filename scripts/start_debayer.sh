#!/bin/bash
ros2 run image_proc debayer_node --ros-args -r /image_raw:=/flir_camera/image_raw -r /image_color:=/camera/color/image_color
