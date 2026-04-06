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
    rs_rgb_profile = LaunchConfiguration("rs_rgb_profile")
    rs_serials = eval(LaunchConfiguration("rs_serials").perform(context))

    usb_serials = eval(LaunchConfiguration("usb_serials").perform(context))

    # Realsense
    rs_nodes = []
    for rs_serial in rs_serials:
        rs_nodes.append(
            Node(
                package='realsense2_camera', 
                executable='realsense2_camera_node',
                name=f'camera_{rs_serial}',
                namespace='/',
                parameters=[{
                                'serial_no': rs_serial,
                                'camera_name': f'camera_{rs_serial}',
                                #'tf_prefix': f'camera_{rs_serial}/', # doesn't work, ros1 only?
                                'rgb_camera.color_profile': rs_rgb_profile,
                                'enable_color': True,
                                'enable_depth': False,
                                'enable_infra1': False,
                                'enable_infra2': False,
                                'enable_gyro': False,
                                'enable_accel': False,
                            }
                ] # parameters
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
