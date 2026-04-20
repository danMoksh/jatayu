from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'jatayu_autonomy'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name] if os.path.exists('resource/' + package_name) else []),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jatayu Development Team',
    maintainer_email='contact@jatayu-uav.org',
    description='Autonomous VTOL Mission Executive & Autonomy Stack',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mission_executive = jatayu_autonomy.mission_executive:main',
            'mavros_bridge = jatayu_autonomy.mavros_bridge:main',
            'target_locator = jatayu_autonomy.target_locator:main',
            'payload_controller = jatayu_autonomy.payload_controller:main',
        ],
    },
)
