import os
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='jatayu_autonomy',
            executable='mavros_bridge',
            name='mavros_bridge',
            output='screen',
            parameters=[{
                'fcu_url': 'tcp:127.0.0.1:5760',
                'gcs_url': '',
                'target_system_id': 1,
                'target_component_id': 1
            }]
        ),
    ])
