from setuptools import setup
import os
from glob import glob

package_name = 'dog2_visualization'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config/rviz'), glob('config/rviz/*.rviz')),
        (os.path.join('share', package_name, 'config/plotjuggler'), glob('config/plotjuggler/*.xml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.world')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dell',
    maintainer_email='dell@todo.todo',
    description='Visualization system for Dog2 quadruped robot',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'visualization_node = dog2_visualization.visualization_node:main',
            'crossing_visualization_node = dog2_visualization.crossing_visualization_node:main',
        ],
    },
)
