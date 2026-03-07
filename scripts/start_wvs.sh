#!/bin/bash
source /opt/ros/humble/setup.bash
echo $$ > /workspaces/vdt/scripts/web_video_server.pid
ros2 run web_video_server web_video_server