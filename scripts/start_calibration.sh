#!/bin/bash

# $1 - camera name
# $2 - chessboard size (inner corners)
# $3 - chessboard square size in meters

source /opt/ros/$ROS_DISTRO/setup.bash

echo $$ > /workspaces/vdt/scripts/calibration.pid

echo "Press Q in calibrator to exit cleanly."

ros2 run camera_calibration cameracalibrator --size ${2:-6x4} --square ${3:-0.030} --no-service-check --camera_name $1 --ros-args --remap camera:=/C$1 --remap image:=/C$1/color/image_raw

if [ -e /tmp/calibrationdata.tar.gz ]; then
    cd /tmp
    
    tar xzf /tmp/calibrationdata.tar.gz
    rm /tmp/calibrationdata.tar.gz

    FileDate=$(date "+%Y%m%d_%H%M%S")
    cp /tmp/ost.yaml /workspaces/vdt/cameras/$1.yaml
    cp /tmp/ost.yaml /workspaces/vdt/cameras/$1.${FileDate}.yaml
else
    echo "No calibration data found."
fi
