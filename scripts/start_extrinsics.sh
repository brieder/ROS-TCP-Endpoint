#!/bin/bash

if [[ -n "${VDTDEV}" || -n "${VDTDEV_EXT}" ]]; then
    source /workspaces/vdt/extrinsic_calibrator/install/setup.bash
else
    source /home/void/extrinsic_calibrator/install/setup.bash
fi

source /home/void/fastervoxelpose/venv/bin/activate

ros2 run extrinsic_calibrator_core extrinsic_calibrator_node.py --ros-args --params-file /workspaces/vdt/configs/extrinsic_calibrator_params.yamlx
