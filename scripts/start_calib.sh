#!/bin/bash
ros2 run camera_calibration cameracalibrator --size 9x6 --square 0.027 --ros-args -r image:=/cam_1/color/image_raw -r camera:=/cam_1/color