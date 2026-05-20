docker run -it --rm --privileged --gpus=all -p 8765:8765 -p 10000:10000 --name=vdt-pb ^
	--mount type=bind,src=./scripts,dst=/workspaces/vdt ^
	--mount type=bind,src=../rosbags,dst=/workspaces/vdt/rosbags ^
    void/vdt-pb
