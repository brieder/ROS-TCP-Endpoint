#!/bin/bash
docker run -it --rm --privileged --gpus=all --net=host --name=vdt-pb \
	--mount type=bind,src=./scripts,dst=/workspaces/vdt \
	--mount type=bind,src=../rosbags,dst=/workspaces/vdt/rosbags \
    void/vdt-pb
