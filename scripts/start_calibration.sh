#!/bin/bash

# $1 - camera name
# $2 - chessboard size (inner corners)
# $3 - chessboard square size in meters

source /opt/ros/humble/setup.bash
echo $$ > /workspaces/vdt/scripts/calibration.pid

echo "Press Q in calibrator to exit cleanly."

ros2 run camera_calibration cameracalibrator --size ${2:-6x4} --square ${3:-0.030} --no-service-check --camera_name $1 --ros-args --remap camera:=/C$1 --remap image:=/C$1/color/image_raw

cd /tmp
tar xvzf /tmp/calibrationdata.tar.gz
cp /tmp/ost.yaml /workspaces/vdt/cameras/$1.yaml