#!/bin/bash
ros2 run usb_cam usb_cam_node_exe --ros-args --remap __ns:=/cam_1/color --params-file ./usb_cam_params_1.yaml