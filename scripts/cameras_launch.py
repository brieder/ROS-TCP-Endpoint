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

import pyudev

def launch_setup(
    context: LaunchContext, *args, **kwargs
) -> list[LaunchDescriptionEntity]:
    enable_color = LaunchConfiguration("enable_color")
    enable_infra1 = LaunchConfiguration("enable_infra1")
    rs_infra_profile = LaunchConfiguration("rs_infra_profile")
    rs_rgb_enable_ae = LaunchConfiguration("rs_rgb_enable_ae")
    rs_rgb_exposure = LaunchConfiguration("rs_rgb_exposure")
    rs_rgb_profile = LaunchConfiguration("rs_rgb_profile")
    rs_serials = eval(LaunchConfiguration("rs_serials").perform(context))
    usb_serials = eval(LaunchConfiguration("usb_serials").perform(context))

    # Realsense
    rs_nodes = []
    for rs_serial in rs_serials:
        #camera_name = f'camera_{rs_serial}'
        camera_name = f'C{rs_serial}'
        rs_nodes.append(
            Node(
                package='realsense2_camera', 
                executable='realsense2_camera_node',
                name=camera_name,
                namespace='/',
                parameters=[{
                                'serial_no': rs_serial,
                                'camera_name': camera_name,
                                #'tf_prefix': f'camera_{rs_serial}/', # doesn't work, ros1 only?
                                'depth_module.infra_profile': rs_infra_profile,
                                'rgb_camera.color_profile': rs_rgb_profile,
                                'rgb_camera.auto_exposure_priority': False,
                                'rgb_camera.enable_auto_exposure': rs_rgb_enable_ae,
                                'rgb_camera.exposure': rs_rgb_exposure,
                                'enable_color': enable_color,
                                'enable_depth': False,
                                'enable_infra1': enable_infra1,
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

        if enable_infra1 is True:
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
    for usb_serial in usb_serials:
        device_name = 'Serial Not Found' # will cause an error
        for device in pyudev_context.list_devices(subsystem='video4linux', ID_SERIAL_SHORT=usb_serial):
            # Example: Brio has 4 devices: rgb, meta, ir, meta. RS has inconsistent order.
            device_name = device.get('DEVNAME')
            break

        usb_nodes.append(
            Node(
                package='usb_cam', 
                executable='usb_cam_node_exe',
                name=f'camera_{usb_serial}',
                namespace=f'/camera_{usb_serial}/color',
                parameters=['./params_usb_cam_1.yaml',
                            {
                                'frame_id': f'camera_{usb_serial}',
                                'video_device': device_name
                            }
                ]
            )
        )

    return [*rs_nodes, *usb_nodes]

def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "enable_color",
            default_value="True",
            description="Enable color stream",
        ),
        DeclareLaunchArgument(
            "enable_infra1",
            default_value="False",
            description="Enable infra1 stream",
        ),
        DeclareLaunchArgument(
            "rs_infra_profile",
            default_value="1280x800x30",
            description="Realsense RGB Color Profile.",
        ),
        DeclareLaunchArgument(
            "rs_rgb_enable_ae",
            default_value="True",
            description="Realsense Enable RGB Auto Exposure",
        ),
        DeclareLaunchArgument(
            "rs_rgb_exposure",
            default_value="156",
            description="Realsense RGB Exposure",
        ),
        DeclareLaunchArgument(
            "rs_rgb_profile",
            default_value="640x480x30",
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
