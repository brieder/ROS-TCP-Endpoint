#!/bin/bash
source /home/void/fastervoxelpose/venv/bin/activate

source /home/void/voxelpose_ros/install/setup.bash

export LD_LIBRARY_PATH=/home/void/fastervoxelpose/venv/lib/python3.10/site-packages/nvidia/cu13/lib:$LD_LIBRARY_PATH

echo $$ > /workspaces/vdt/scripts/voxelpose.pid

ros2 run voxelpose_ros voxelpose_node  --ros-args --params-file /workspaces/vdt/configs/voxelpose_params.yamlx
