from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction
)
from launch.conditions import IfCondition
from launch.launch_context import LaunchContext
from launch.launch_description_entity import LaunchDescriptionEntity
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

import parse
import yaml

def launch_setup(
    context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:

    enable_extrinsics = LaunchConfiguration("enable_extrinsics")
    enable_tcp = LaunchConfiguration("enable_tcp")
    enable_voxelpose = LaunchConfiguration("enable_voxelpose")
    enable_wvs = LaunchConfiguration("enable_wvs")

    use_infrared = LaunchConfiguration("rs_enable_infra1").perform(context) # string

    rs_infra_profile = LaunchConfiguration("rs_infra_profile").perform(context)
    rs_rgb_profile = LaunchConfiguration("rs_rgb_profile").perform(context)
    
    # RS and USB cameras launch
    cameras_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource("scripts/launch_cameras.py"),
        launch_arguments={
            "cameras_file": LaunchConfiguration("cameras_file"),
            "rs_qos_sensor_data": LaunchConfiguration("rs_qos_sensor_data"),

            "rs_enable_color": LaunchConfiguration("rs_enable_color"),
            "rs_enable_depth": LaunchConfiguration("rs_enable_depth"),
            "rs_enable_infra1": LaunchConfiguration("rs_enable_infra1"),

            "rs_infra_enable_ae": LaunchConfiguration("rs_infra_enable_ae"),
            "rs_infra_exposure": LaunchConfiguration("rs_infra_exposure"),
            "rs_infra_profile": LaunchConfiguration("rs_infra_profile"),
            "rs_rgb_enable_ae": LaunchConfiguration("rs_rgb_enable_ae"),
            "rs_rgb_exposure": LaunchConfiguration("rs_rgb_exposure"),
            "rs_rgb_gain": LaunchConfiguration("rs_rgb_gain"),
            "rs_rgb_profile": LaunchConfiguration("rs_rgb_profile"),
        }.items(),
    )

    # fox
    foxbridge_node = Node(
        package="foxglove_bridge",
        executable="foxglove_bridge",
        name="foxglove_bridge",
    )

    # Unity tcp endpoint
    tcp_node = Node(
        condition=IfCondition(enable_tcp),
        package="ros_tcp_endpoint",
        executable="default_server_endpoint",
        name="unity_tcp_connector",
        arguments=[ "ROS_IP", "0.0.0.0" ],
    )

    # web video server
    wvs_node = Node(
        condition=IfCondition(enable_wvs),
        package="web_video_server",
        executable="web_video_server",
        name="web_video_server",
        arguments=[],
    )

    cameras_file = LaunchConfiguration("cameras_file")
    with open(cameras_file.perform(context), 'r') as file:
        serial_list = yaml.safe_load(file)    

    # setup the extrinsics params file with the cameras
    extrinsics_params_path = LaunchConfiguration("extrinsics_params_path").perform(context)
    extrinsics_params_path_procd = extrinsics_params_path + "x"
    with open(extrinsics_params_path, 'r') as file:
        params_data = yaml.safe_load(file)    

        cameras = dict()
        for serial, flags in serial_list.items():

            # extrinsics flag defaults True, skip if it's set to False.
            if flags and 'extrinsics' in flags and flags["extrinsics"] == False:
                continue

            camera = dict()
            if use_infrared == "True":
                camera['camera_info_topic'] = f"/C{serial}/infra1/camera_info"
                camera['image_topic'] = f"/C{serial}/infra1/image_rect_raw"
            else:
                camera['camera_info_topic'] = f"/C{serial}/color/camera_info"
                camera['image_topic'] = f"/C{serial}/color/image_raw"
            cameras[f"C{serial}"] = camera

        params_data['/**']['ros__parameters']['cameras'] = cameras

        with open(extrinsics_params_path_procd, 'w') as file:
            yaml.dump(params_data, file)

    # extrinsics calibrator
    extrinsics_node = TimerAction(
        period=5.0, # delay in secs
        actions=[
            Node(
                condition=IfCondition(enable_extrinsics),
                package="extrinsic_calibrator_core",
                executable="extrinsic_calibrator_node.py",
                name="extrinsic_calibrator",
                parameters=[extrinsics_params_path_procd],
            )
        ]
    )

    # happypose params
    ncameras = 0
    happypose_params_path = LaunchConfiguration("happypose_params_path").perform(context)
    happypose_params_path_procd = happypose_params_path + "x"
    with open(happypose_params_path, 'r') as file:
        params_data = yaml.safe_load(file)    

        # camera names and list
        camera_names = []
        cameras = dict()
        leading = True
        for serial, flags in serial_list.items():

            # happypose flag defaults False
            if not flags or not 'happypose' in flags or flags["happypose"] == False:
                continue

            camera_names.append(f"C{serial}")

            camera = dict()
            camera['leading'] = (ncameras == 0)

            cameras[f"C{serial}"] = camera
            ncameras += 1

        cameras['n_min_cameras'] = ncameras

        params_data['/**']['ros__parameters']['camera_names'] = camera_names
        params_data['/**']['ros__parameters']['cameras'] = cameras

        with open(happypose_params_path_procd, 'w') as file:
            yaml.dump(params_data, file)

    # voxelpose params
    ncameras = 0
    voxelpose_params_path = LaunchConfiguration("voxelpose_params_path").perform(context)
    voxelpose_params_path_procd = voxelpose_params_path + "x"
    with open(voxelpose_params_path, 'r') as file:
        params_data = yaml.safe_load(file)    

        # grab the config file path for later and save the modified one in params
        voxelpose_config_path = params_data['/**']['ros__parameters']['voxelpose']['config_file']
        voxelpose_config_path_procd = voxelpose_config_path + "x"
        params_data['/**']['ros__parameters']['voxelpose']['config_file'] = voxelpose_config_path_procd

        # camera names and list
        camera_names = []
        cameras = dict()
        leading = True
        for serial, flags in serial_list.items():

            # voxelpose flag defaults False
            if not flags or not 'voxelpose' in flags or flags["voxelpose"] == False:
                continue

            camera_names.append(f"C{serial}")

            camera = dict()
            camera['leading'] = (ncameras == 0)
            if use_infrared == "True":
                camera['infrared'] = True

            cameras[f"C{serial}"] = camera
            ncameras += 1

        cameras['n_min_cameras'] = ncameras

        params_data['/**']['ros__parameters']['camera_names'] = camera_names
        params_data['/**']['ros__parameters']['cameras'] = cameras

        # save
        with open(voxelpose_params_path_procd, 'w') as file:
            yaml.dump(params_data, file)

    # voxelpose config
    with open(voxelpose_config_path, 'r') as file:
        config_data = yaml.safe_load(file)    
        
        # num cameras
        config_data['DATASET']['CAMERA_NUM'] = ncameras

        if use_infrared == "True":
            result = parse.parse('{width}x{height}x{fps}', rs_infra_profile)
        else:
            result = parse.parse('{width}x{height}x{fps}', rs_rgb_profile)
            
        # image size
        config_data['DATASET']['ORI_IMAGE_SIZE'] = [ int(result['width']), int(result['height']) ]

        # save
        with open(voxelpose_config_path_procd, 'w') as file:
            yaml.dump(config_data, file)

    # voxelpose
    voxelpose_node = Node(
        condition=IfCondition(enable_voxelpose),
        package="voxelpose_ros",
        executable="voxelpose_node",
        name="voxelpose_node",
        parameters=[voxelpose_params_path_procd],
    )

    return [cameras_launch, foxbridge_node, tcp_node, wvs_node, extrinsics_node, voxelpose_node]

def generate_launch_description():
    declared_arguments = [
        # Cameras File
        DeclareLaunchArgument(
            "cameras_file",
            default_value="cameras.yaml",
            description="Yaml file full of cameras.",
        ),
        DeclareLaunchArgument(
            "extrinsics_params_path",
            default_value="./configs/extrinsic_calibrator_params.yaml",
            description="Path to a file containing extrinsics_calibrator node parameters.",
        ),
        DeclareLaunchArgument(
            "happypose_params_path",
            default_value="./configs/happypose_params.yaml",
            description="Path to a file containing happypose_ros node parameters.",
        ),
        DeclareLaunchArgument(
            "voxelpose_params_path",
            default_value="./configs/voxelpose_params.yaml",
            description="Path to a file containing voxelpose node parameters.",
        ),

        DeclareLaunchArgument(
            "enable_extrinsics",
            default_value="True",
            description="Enable Extrinsic Calibrator.",
        ),
        DeclareLaunchArgument(
            "enable_tcp",
            default_value="True",
            description="Enable Unity ROS TCP Endpoint.",
        ),
        DeclareLaunchArgument(
            "enable_voxelpose",
            default_value="False",
            description="Enable Voxelpose.",
        ),
        DeclareLaunchArgument(
            "enable_wvs",
            default_value="True",
            description="Enable Web Video Server.",
        ),

        DeclareLaunchArgument(
            "rs_qos_sensor_data",
            default_value="True",
            description="Use SENSOR_DATA for Realsense QOS.",
        ),

        # Cameras Launch
        DeclareLaunchArgument(
            "rs_enable_color",
            default_value="True",
            description="Realsense Enable color stream",
        ),
        DeclareLaunchArgument(
            "rs_enable_depth",
            default_value="False",
            description="Realsense Enable depth stream",
        ),
        DeclareLaunchArgument(
            "rs_enable_infra1",
            default_value="False",
            description="Realsense Enable infra1 stream",
        ),

        DeclareLaunchArgument(
            "rs_infra_enable_ae",
            default_value="False",
            description="Realsense Enable RGB Auto Exposure",
        ),
        DeclareLaunchArgument(
            "rs_infra_exposure",
            default_value="17000",
            description="Realsense Infrared Exposure",
        ),
        DeclareLaunchArgument(
            "rs_infra_profile",
            default_value="1280x800x15",
            description="Realsense RGB Color Profile.",
        ),

        DeclareLaunchArgument(
            "rs_rgb_enable_ae",
            default_value="False",
            description="Realsense Enable RGB Auto Exposure",
        ),
        DeclareLaunchArgument(
            "rs_rgb_exposure",
            default_value="312",
            description="Realsense RGB Exposure",
        ),
        DeclareLaunchArgument(
            "rs_rgb_gain",
            default_value="64",
            description="Realsense RGB Gain",
        ),
        DeclareLaunchArgument(
            "rs_rgb_profile",
            default_value="960x540x60",
            description="Realsense RGB Color Profile.",
        ),

        DeclareLaunchArgument(
            "rs_serials",
            default_value="[]",
            description="List of Realsense serials.",
        ),
        DeclareLaunchArgument(
            "usb_serials",
            default_value="[]",
            description="List of Realsense serials.",
        ),
    ]

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
