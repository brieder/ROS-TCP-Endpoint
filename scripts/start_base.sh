#!/bin/bash

# See if disable-usbfs-check is set.
# while [[ $# -gt 0 ]]; do
# case "$1" in
# --disable-usbfs-check)
# echo "Disabling usbfs memory check."
# DISABLE_USBFS_CHECK=1
# ;;
# esac
# shift 1  # Move to the next argument
# done

# usfs memory check
USBFS_MEMORY_LIMIT=1024
USBFS_MEMORY=$(cat /sys/module/usbcore/parameters/usbfs_memory_mb)
if [ "$USBFS_MEMORY" -lt "$USBFS_MEMORY_LIMIT" ] && [ -z $DISABLE_USBFS_CHECK ]; then
    echo "ERROR: /sys/module/usbcore/parameters/usbfs_memory_mb ($USBFS_MEMORY) is less than $USBFS_MEMORY_LIMIT."
    echo "Use --disable-usbfs-check to ignore this check."
    # echo "1024" | sudo tee /sys/module/usbcore/parameters/usbfs_memory_mb
    exit
fi

# fox and tcp: voxelpose msgs
if [[ -n "${VDTDEV}" || -n "${VDTDEV_VPR}" ]]; then
    source /workspaces/vdt/voxelpose_ros/install/setup.bash
else
    source /home/void/voxelpose_ros/install/setup.bash
fi

source /home/void/happypose_ros/install/setup.bash

# tcp
source /home/void/ROS-TCP-Endpoint/install/setup.bash

# usb_cam
if [[ -n "${VDTDEV}" || -n "${VDTDEV_USB}" ]]; then
    source /workspaces/vdt/usb_cam/install/setup.bash
else
    source /home/void/usb_cam/install/setup.bash
fi

# ext
if [[ -n "${VDTDEV}" || -n "${VDTDEV_EXT}" ]]; then
    source /workspaces/vdt/extrinsic_calibrator/install/setup.bash
else
    source /home/void/extrinsic_calibrator/install/setup.bash
fi

# VP python venv (won't work for happy)
source /home/void/fastervoxelpose/venv/bin/activate

# libcudart.so.13 ldpath hack, the order is wrong somewhere.
export LD_LIBRARY_PATH=/home/void/fastervoxelpose/venv/lib/python3.10/site-packages/nvidia/cu13/lib:$LD_LIBRARY_PATH

ros2 launch /workspaces/vdt/scripts/launch_base.py $*
