from setuptools import setup

package_name = 'autonomous_vehicle'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/autonomous_vehicle_launch.py']),
        ('share/' + package_name + '/worlds', ['worlds/simple_world.sdf']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='metasebiya8@gmail.com',
    description='Autonomous vehicle stack for class assignment',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rcnn_localization = autonomous_vehicle.rcnn_localization:main',
            'sensor_fusion = autonomous_vehicle.sensor_fusion:main',
            'path_planning = autonomous_vehicle.path_planning:main',
            'simple_control = autonomous_vehicle.simple_control:main',
        ],
    },
)