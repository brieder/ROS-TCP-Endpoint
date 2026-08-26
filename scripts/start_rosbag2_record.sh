#!/bin/bash
source /opt/ros/humble/setup.bash

# for voxelpose_msgs
source /home/void/voxelpose_ros/install/setup.bash

# "defaults to a timestamped folder in the current directory"
mkdir -p /workspaces/vdt/rosbags
cd /workspaces/vdt/rosbags

echo $$ > /workspaces/vdt/scripts/rosbag2_recorder.pid

ros2 bag record --storage mcap $*