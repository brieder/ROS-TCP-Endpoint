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
    camera_serials = eval(LaunchConfiguration("camera_serials").perform(context))

    # Realsense
    apriltag_nodes = []
    for cam_serial in camera_serials:
        camera_name = f'C{cam_serial}'
        tag_frame_str = f'{camera_name}:14'
        apriltag_nodes.append(
            Node(
                package='apriltag_ros', 
                executable='apriltag_node',
                name=f'apriltag_{cam_serial}',
                #namespace='/',
                parameters=['./configs/apriltag_36h11.yaml',
                            {
                                'tag.frames': [ tag_frame_str ] 
                            }
                ],
                remappings=[
                            ('image_rect', f'/{camera_name}/color/image_raw'),
                            ('camera_info', f'/{camera_name}/color/camera_info'),
                            ('detections', 'apriltag_detections')
                ]
            ) # Node
        ) # append

    return [*apriltag_nodes]

def generate_launch_description():
    declared_arguments = [
        DeclareLaunchArgument(
            "camera_serials",
            default_value="[]",
            description="List of camera serials to run detection on.",
        ),
    ]

    return LaunchDescription(
        declared_arguments + [OpaqueFunction(function=launch_setup)]
    )
