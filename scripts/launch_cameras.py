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
    
    # realsense
    rs_qos_sensor_data = LaunchConfiguration("rs_qos_sensor_data")
    rs_enable_color = LaunchConfiguration("rs_enable_color")
    rs_enable_depth = LaunchConfiguration("rs_enable_depth")
    rs_enable_infra1 = LaunchConfiguration("rs_enable_infra1")
    rs_infra_enable_ae = LaunchConfiguration("rs_infra_enable_ae")
    rs_infra_exposure = LaunchConfiguration("rs_infra_exposure")
    rs_infra_profile = LaunchConfiguration("rs_infra_profile")
    rs_rgb_enable_ae = LaunchConfiguration("rs_rgb_enable_ae")
    rs_rgb_exposure = LaunchConfiguration("rs_rgb_exposure")
    rs_rgb_gain = LaunchConfiguration("rs_rgb_gain")
    rs_rgb_profile = LaunchConfiguration("rs_rgb_profile")

    # basler pylon
    pylon_rgb_profile = LaunchConfiguration("pylon_rgb_profile").perform(context)

    # uvc
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
        params_dict = {
            'serial_no': serial,
            'camera_name': camera_name,

            'depth_module.infra_profile': rs_infra_profile,
            'depth_module.enable_auto_exposure': rs_infra_enable_ae,
            'depth_module.exposure': rs_infra_exposure,

            'rgb_camera.color_profile': rs_rgb_profile,
            'rgb_camera.auto_exposure_priority': False,
            'rgb_camera.enable_auto_exposure': rs_rgb_enable_ae,
            'rgb_camera.exposure': rs_rgb_exposure,
            'rgb_camera.gain': rs_rgb_gain,

            'enable_color': rs_enable_color,
            'enable_depth': rs_enable_depth,
            'enable_infra1': rs_enable_infra1,
            'enable_infra2': False,
            'enable_gyro': False,
            'enable_accel': False,

            'publish_tf': False,

            # turn off emitter
            'depth_module.emitter_enabled': 0,
            'depth_module.laser_power': 0.0,
        }
        
        if rs_qos_sensor_data.perform(context) == "True":
            qos_sensors_dict = { 
                'color_info_qos': 'SENSOR_DATA', 
                'color_qos': 'SENSOR_DATA'
            }
            params_dict.update(qos_sensors_dict)

        rs_nodes.append(
            Node(
                package='realsense2_camera', 
                executable='realsense2_camera_node',
                name=camera_name,
                namespace='/',
                parameters=[params_dict]
            ) # Node
        ) # append

        # static transform linking camera link to external camera positoin.
        if rs_enable_infra1.perform(context) == "True":
            color_child_frame = f'{camera_name}_infra1_optical_frame'
        else:
            color_child_frame = f'{camera_name}_color_optical_frame'
            #color_child_frame = f'{camera_name}_link'
        rs_nodes.append(
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name=f"static_transform_publisher_color_{camera_name}",
                arguments=[
                    "--roll", "-1.57",
                    "--yaw", "-1.57",
                    "--frame-id", camera_name,
                    "--child-frame-id", color_child_frame,
                ],
            ) # Node
        ) # append

        if rs_enable_depth.perform(context) == "True":
            depth_child_frame = f'{camera_name}_depth_optical_frame'
            rs_nodes.append(
                Node(
                    package="tf2_ros",
                    executable="static_transform_publisher",
                    name=f"static_transform_publisher_depth_{camera_name}",
                    arguments=[
                        "--roll", "-1.57",
                        "--yaw", "-1.57",
                        "--frame-id", camera_name,
                        "--child-frame-id", depth_child_frame,
                    ],
                ) # Node
            ) # append

    # Pylon
    pylon_nodes = []
    for serial, options in cameras.items():
        if not options or not 'type' in options or options['type'] != 'pylon':
            continue

        camera_name = f'C{serial}'
        pylon_nodes.append(
            Node(
                package='pylon_ros2_camera_wrapper', 
                executable='pylon_ros2_camera_wrapper',
                namespace=camera_name,
                name='color',
                parameters=['./configs/camera_pylon.yaml',
                            {
                                'camera_frame': f'{camera_name}_color_optical_frame',
                                'camera_info_url': f'file:///workspaces/vdt/cameras/{serial}.yaml',
                                'device_user_id': serial,
                            }
                ] # parameters
            ) # Node
        ) # append

        enable_debayer = True
        if enable_debayer:
            pylon_nodes.append(
                Node(
                    package="image_proc",
                    executable="debayer_node",
                    name=f"debayer_node_{camera_name}",
                    remappings=[
                                ('image_raw', f'/{camera_name}/color/image_raw'),
                                ('image_color', f'/{camera_name}/color/image_color'),
                    ]
                ) # Node
            ) # append

        # Add optical_frame for pylon cameras.
        color_child_frame = f'{camera_name}_color_optical_frame'
        pylon_nodes.append(
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name=f"static_transform_publisher_color_{camera_name}",
                arguments=[
                    "--roll", "-1.57",
                    "--yaw", "-1.57",
                    "--frame-id", camera_name,
                    "--child-frame-id", color_child_frame,
                ],
            ) # Node
        ) # append

    # USB
    pyudev_context = pyudev.Context()
    usb_nodes = []
    usb_rgb_profile_parse = parse.parse('{width}x{height}x{fps}', usb_rgb_profile)
    for serial, options in cameras.items():
        # usb flag defaults False
        if not options or not 'type' in options or options['type'] != 'usb':
            continue

        # device overrides serial
        if 'device' in options: 
            video_device = options['device']
        else:
            video_device = None
        if 'format' in options: 
            format = options['format']
        else:
            format = 'mjpeg2rgb' # or yuyv

        # width, height, fps, format, options override profile
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
        # ae / af
        # exposure
        
        if video_device:
            device_name = video_device
        else:
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

                name='usb',
                namespace=f'/{camera_name}/color',

                #arguments=['--ros-args', '--log-level', 'debug'],
                #parameters=[f'./configs/camera_usb_yuyv.yaml',
                parameters=[f'./configs/camera_usb_mjpeg.yaml',
                            {
                                'camera_info_url': f'file:///workspaces/vdt/cameras/{serial}.yaml',
                                'camera_name': camera_name,
                                'frame_id': f'{camera_name}_color_optical_frame',
                                'framerate': fps,
                                'image_width': width,
                                'image_height': height,
                                'pixel_format': format,
                                'video_device': device_name
                            }
                ]
            )
        )

        # add optical_frame for usb cameras
        color_child_frame = f'{camera_name}_color_optical_frame'
        usb_nodes.append(
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                name=f"static_transform_publisher_color_{camera_name}",
                arguments=[
                    "--roll", "-1.57",
                    "--yaw", "-1.57",
                    "--frame-id", camera_name,
                    "--child-frame-id", color_child_frame,
                ],
            ) # Node
        ) # append


    return [*rs_nodes, *pylon_nodes, *usb_nodes]

def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "cameras_file",
            default_value="cameras.yaml",
            description="Yaml file full of cameras.",
        ),

        DeclareLaunchArgument(
            "rs_qos_sensor_data",
            default_value="True",
            description="Use SENSOR_DATA for Realsense QOS.",
        ),

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
            "pylon_rgb_profile",
            default_value="960x540x60",
            description="Basler Pylon RGB Profile.",
        ),

        DeclareLaunchArgument(
            "usb_rgb_profile",
            default_value="960x540x30",
            description="USB RGB Color Profile.",
        ),
    ]

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
