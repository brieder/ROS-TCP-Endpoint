#!/bin/bash

# for voxelpose_msgs
source /home/void/voxelpose_ros/install/setup.bash

/workspaces/vdt/scripts/start_rosbag2_record.sh --regex voxelpose $*