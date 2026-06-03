#!/bin/bash

source /home/void/voxelpose_ros/install/setup.bash

ros2 bag play --loop $*
