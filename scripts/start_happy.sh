#!/bin/bash

source /home/void/miniconda3/bin/activate
conda activate happypose

#export CUDA_VISIBLE_DEVICES=1
#export EGL_VISIBLE_DEVICES=1

export HAPPYPOSE_DATA_DIR=/workspaces/vdt/data/happypose
export LD_LIBRARY_PATH=/home/void/miniconda3/lib:$LD_LIBRARY_PATH

source /home/void/happypose_ros/install/setup.bash
#source /workspaces/vdt/happypose_ros/install/setup.bash

export PYTHONPATH=/home/void/miniconda3/envs/happypose/lib/python3.10/site-packages:$PYTHONPATH

echo $$ > /workspaces/vdt/scripts/happypose.pid

ros2 run happypose_ros happypose_node  --ros-args --params-file /workspaces/vdt/configs/happypose_params.yamlx
