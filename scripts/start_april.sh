#!/bin/bash
ros2 run apriltag_ros apriltag_node --ros-args -r image_rect:=/cam_1/image_raw -r camera_info:=/cam_1/camera_info --params-file ./tags_36h11.yaml