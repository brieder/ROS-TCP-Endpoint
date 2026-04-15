#!/bin/bash
ros2 launch ./scripts/cameras_launch.py rs_serials:="['814412071982', '829212072304', '829212072337', '843112071706']" enable_color:=False enable_infra1:=True $*
