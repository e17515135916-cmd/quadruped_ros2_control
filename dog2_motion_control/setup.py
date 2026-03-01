from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'dog2_motion_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=[
        'setuptools',
        'numpy>=1.20.0',
        'scipy>=1.7.0',
    ],
    zip_safe=True,
    maintainer='Developer',
    maintainer_email='dev@example.com',
    description='Spider robot basic motion control system with crawl gait implementation',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'spider_controller = dog2_motion_control.spider_robot_controller:main',
        ],
    },
)
