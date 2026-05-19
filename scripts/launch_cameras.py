from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
)
from launch.launch_context import LaunchContext
from launch.launch_description_entity import LaunchDescriptionEntity
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import parse
import pyudev # usb serials
import yaml

def launch_setup(
    context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    cameras_file = LaunchConfiguration("cameras_file")
    
    rs_enable_color = LaunchConfiguration("rs_enable_color")
    rs_enable_infra1 = LaunchConfiguration("rs_enable_infra1")
    rs_infra_enable_ae = LaunchConfiguration("rs_infra_enable_ae")
    rs_infra_exposure = LaunchConfiguration("rs_infra_exposure")
    rs_infra_profile = LaunchConfiguration("rs_infra_profile")
    rs_rgb_enable_ae = LaunchConfiguration("rs_rgb_enable_ae")
    rs_rgb_exposure = LaunchConfiguration("rs_rgb_exposure")
    rs_rgb_profile = LaunchConfiguration("rs_rgb_profile")

    usb_rgb_profile = LaunchConfiguration("usb_rgb_profile").perform(context)

    cameras_file = LaunchConfiguration("cameras_file")
    with open(cameras_file.perform(context), 'r') as file:
        cameras = yaml.safe_load(file)    

    # Realsense
    rs_nodes = []
    for serial, options in cameras.items():
        # realsense flag defaults False
        if not options or not 'type' in options or options['type'] != 'realsense':
            continue

        camera_name = f'C{serial}'
        rs_nodes.append(
            Node(
                package='realsense2_camera', 
                executable='realsense2_camera_node',
                name=camera_name,
                namespace='/',
                parameters=[{
                                'serial_no': serial,
                                'camera_name': camera_name,

                                'depth_module.infra_profile': rs_infra_profile,
                                'depth_module.enable_auto_exposure': rs_infra_enable_ae,
                                'depth_module.exposure': rs_infra_exposure,

                                'rgb_camera.color_profile': rs_rgb_profile,
                                'rgb_camera.auto_exposure_priority': False,
                                'rgb_camera.enable_auto_exposure': rs_rgb_enable_ae,
                                'rgb_camera.exposure': rs_rgb_exposure,

                                'enable_color': rs_enable_color,
                                'enable_depth': False,
                                'enable_infra1': rs_enable_infra1,
                                'enable_infra2': False,
                                'enable_gyro': False,
                                'enable_accel': False,

                                'publish_tf': False,

                                'depth_module.emitter_enabled': 0,
                                'depth_module.laser_power': 0.0,

                                'color_info_qos': 'SENSOR_DATA',
                                'color_qos': 'SENSOR_DATA',
                            }
                ] # parameters
            ) # Node
        ) # append

        if rs_enable_infra1.perform(context) == "True":
            child_frame = f'{camera_name}_infra1_optical_frame'
        else:
            child_frame = f'{camera_name}_color_optical_frame'

        rs_nodes.append(
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name=f"static_transform_publisher_{camera_name}",
                arguments=[
                    # "--roll", "-1.57",
                    # "--yaw", "-1.57",
                    "--frame-id", camera_name,
                    "--child-frame-id", child_frame,
                ],
            ) # Node
        ) # append

    pyudev_context = pyudev.Context()

    # USB
    usb_nodes = []
    usb_rgb_profile_parse = parse.parse('{width}x{height}x{fps}', usb_rgb_profile)
    for serial, options in cameras.items():
        # usb flag defaults False
        if not options or not 'type' in options or options['type'] != 'usb':
            continue

        # check options for width, height, fps, format, options override profile
        if 'width' in options: 
            width = options['width']
        else:
            width = int(usb_rgb_profile_parse['width'])
        if 'height' in options: 
            height = options['height']
        else:
            height = int(usb_rgb_profile_parse['height'])
        if 'fps' in options: 
            fps = options['fps']
        else:
            fps = float(usb_rgb_profile_parse['fps'])
        if 'format' in options: 
            format = options['format']
        else:
            format = 'mjpeg2rgb' # or yuyv
        # ae / af
        # exposure
        
        device_name = 'Serial Not Found' # will cause an error
        for device in pyudev_context.list_devices(subsystem='video4linux', ID_SERIAL_SHORT=serial):
            # Example: Brio has 4 devices: rgb, meta, ir, meta. RS has inconsistent order.
            device_name = device.get('DEVNAME')
            break

        camera_name = f'C{serial}'
        usb_nodes.append(
            Node(
                package='usb_cam', 
                executable='usb_cam_node_exe',
                #name=camera_name,
                namespace=f'/{camera_name}/color',
                #arguments=['--ros-args', '--log-level', 'debug'],
                #parameters=[f'./configs/camera_usb_yuyv.yaml',
                parameters=[f'./configs/camera_usb_mjpeg.yaml',
                            {
                                'camera_info_url': f'file:///workspaces/vdt/cameras/{serial}.yaml',
                                'camera_name': camera_name,
                                'frame_id': camera_name,
                                'image_width': width,
                                'image_height': height,
                                'fps': fps,
                                'pixel_format': format,
                                'video_device': device_name
                            }
                ]
            )
        )

    return [*rs_nodes, *usb_nodes]

def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "cameras_file",
            default_value="cameras.yaml",
            description="Yaml file full of cameras.",
        ),

        DeclareLaunchArgument(
            "rs_enable_color",
            default_value="True",
            description="Realsense Enable color stream",
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
            default_value="8500",
            description="Realsense Infrared Exposure",
        ),
        DeclareLaunchArgument(
            "rs_infra_profile",
            default_value="1280x800x30",
            description="Realsense RGB Color Profile.",
        ),

        DeclareLaunchArgument(
            "rs_rgb_enable_ae",
            default_value="False",
            description="Realsense Enable RGB Auto Exposure",
        ),
        DeclareLaunchArgument(
            "rs_rgb_exposure",
            default_value="156",
            description="Realsense RGB Exposure",
        ),
        DeclareLaunchArgument(
            "rs_rgb_profile",
            default_value="960x540x60",
            description="Realsense RGB Color Profile.",
        ),

        DeclareLaunchArgument(
            "usb_rgb_profile",
            default_value="960x540x60",
            description="USB RGB Color Profile.",
        ),
    ]

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
