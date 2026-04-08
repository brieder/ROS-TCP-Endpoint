:: Batch file to run the VDT container in standalone mode on Windows

docker run -it --rm --privileged --gpus=all --net=host --name=vdt ^
	-e DISPLAY=:0 ^
	-e WAYLAND_DISPLAY=wayland-0 ^
	-e XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir ^
	-e ROS_AUTOMATIC_DISCOVERY_RANGE="SUBNET" ^
	-e ROS_DOMAIN_ID="42" ^
	--mount type=bind,src=.,dst=/workspaces/vdt ^
	-v /run/desktop/mnt/host/wslg/.X11-unix:/tmp/.X11-unix ^
	-v /run/desktop/mnt/host/wslg:/mnt/wslg ^
    brieder/vdt /bin/bash