from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-v', '4', '-r', '/home/metasebiya/autonomous_vehicle_ws/src/autonomous_vehicle/worlds/simple_world.sdf'],
            output='screen'
        ),
        ExecuteProcess(
            cmd=['ros2', 'run', 'ros_ign_bridge', 'parameter_bridge',
                 '/camera/image_raw@sensor_msgs/msg/Image@ignition.msgs.Image',
                 '/lidar/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
                 '/imu/data@sensor_msgs/msg/Imu@ignition.msgs.IMU',
                 '/gps/fix@sensor_msgs/msg/NavSatFix@ignition.msgs.NavSat'],
            output='screen'
        ),
        Node(
            package='autonomous_vehicle',
            executable='rcnn_localization',
            name='rcnn_localization_node',
            output='screen'
        ),
        Node(
            package='autonomous_vehicle',
            executable='sensor_fusion',
            name='sensor_fusion_node',
            output='screen'
        ),
        Node(
            package='autonomous_vehicle',
            executable='path_planning',
            name='path_planning_node',
            output='screen'
        ),
        Node(
            package='autonomous_vehicle',
            executable='simple_control',
            name='simple_control_node',
            output='screen'
        ),
    ])