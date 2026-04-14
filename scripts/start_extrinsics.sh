#!/bin/bash
source /home/void/extrinsic_calibrator/install/setup.bash
source /home/void/fastervoxelpose/venv/bin/activate
ros2 run extrinsic_calibrator_core extrinsic_calibrator_node.py --ros-args --params-file /workspaces/vdt/configs/extrinsic_calibrator_params.yaml
