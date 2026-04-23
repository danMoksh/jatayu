import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    params_file = os.path.join(
        get_package_share_directory('jatayu_autonomy'),
        'config',
        'vtol_mission_params.yaml'
    )

    return LaunchDescription([
        Node(
            package='jatayu_autonomy',
            executable='mission_executive',
            name='mission_executive',
            output='screen',
            parameters=[params_file]
        ),
        Node(
            package='jatayu_autonomy',
            executable='mavros_bridge',
            name='mavros_bridge',
            output='screen'
        ),
        Node(
            package='jatayu_autonomy',
            executable='target_locator',
            name='target_locator',
            output='screen',
            parameters=[params_file]
        ),
        Node(
            package='jatayu_autonomy',
            executable='payload_controller',
            name='payload_controller',
            output='screen',
            parameters=[params_file]
        ),
    ])
