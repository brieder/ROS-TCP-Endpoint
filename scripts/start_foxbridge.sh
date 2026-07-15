#!/bin/bash
# Need the voxelpose msgs.
source /home/void/voxelpose_ros/install/setup.bash
echo $$ > /workspaces/vdt/scripts/foxglove_bridge.pid
ros2 launch foxglove_bridge foxglove_bridge_launch.xml