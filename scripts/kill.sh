#!/bin/bash
# kill script for launcher (matches start scripts)
pid=$(cat "/workspaces/vdt/scripts/$1.pid")
echo Sending TERM to pid group: $pid
sudo kill -TERM -- -$pid
