#!/bin/bash

# fox and tcp: voxelpose msgs
#source /home/void/voxelpose_ros/install/setup.bash
source /workspaces/vdt/voxelpose_ros/install/setup.bash

# tcp
source /home/void/ROS-TCP-Endpoint/install/setup.bash

# ext
source /home/void/extrinsic_calibrator/install/setup.bash

# VP python venv (won't work for happy)
source /home/void/fastervoxelpose/venv/bin/activate

# libcudart.so.13 ldpath hack, the order is wrong somewhere.
export LD_LIBRARY_PATH=/home/void/fastervoxelpose/venv/lib/python3.10/site-packages/nvidia/cu13/lib:$LD_LIBRARY_PATH

ros2 launch /workspaces/vdt/scripts/vp_all.py $*
