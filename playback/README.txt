1. Build the container (need BUILDTOKEN in ../.devcontainer): 
	.\pb_build.bat
	
2. Launch the container (container will remove on close):
	.\pb_run.bat

In Container:

3. Launch the base (foxbridge and Unity Connector).
	./go_base.sh
	
4. Play the rosbag (loops):
	./go_playbag.sh rosbags/{rosbag_dirname}

ros2 bag play controls:	
Press SPACE for Pause/Resume
Press CURSOR_RIGHT for Play Next Message
Press CURSOR_UP for Increase Rate 10%
Press CURSOR_DOWN for Decrease Rate 10%	