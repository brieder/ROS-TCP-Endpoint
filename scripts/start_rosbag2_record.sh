#!/bin/bash
source /opt/ros/humble/setup.bash
echo $$ > /workspaces/vdt/scripts/rosbag2_recorder.pid
# "defaults to a timestamped folder in the current directory"
mkdir -p /workspaces/vdt/rosbags
cd /workspaces/vdt/rosbags
ros2 bag record --compression-format=zstd --compression-mode=message $*