#!/bin/bash
source /opt/ros/humble/setup.bash
echo $$ > /workspaces/vdt/scripts/rosbridge_websocket.pid
ros2 launch rosbridge_server rosbridge_websocket_launch.xml