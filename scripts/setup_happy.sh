#!/bin/bash

source /home/void/miniconda3/bin/activate
conda activate happypose

#export CUDA_VISIBLE_DEVICES=1
#export EGL_VISIBLE_DEVICES=1

export HAPPYPOSE_DATA_DIR=/home/void/happypose_data
export LD_LIBRARY_PATH=/home/void/miniconda3/lib:$LD_LIBRARY_PATH

#source /opt/ros/humble/setup.bash
#source /home/void/happypose_ros/install/setup.bash
source /workspaces/vdt/happypose_ros/install/setup.bash

export PYTHONPATH=/home/void/miniconda3/envs/happypose/lib/python3.10/site-packages:$PYTHONPATH
