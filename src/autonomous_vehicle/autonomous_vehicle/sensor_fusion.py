import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, NavSatFix
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
import numpy as np

class SensorFusionNode(Node):
    def __init__(self):
        super().__init__('sensor_fusion_node')
        self.pose_sub = self.create_subscription(
            PoseStamped, '/localization/pose', self.pose_callback, 10)
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.gps_sub = self.create_subscription(
            NavSatFix, '/gps/fix', self.gps_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odometry/filtered', 10)
        self.state = np.zeros(5)  # [x, y, theta, vx, vy]
        self.covariance = np.eye(5) * 0.1
        self.last_time = self.get_clock().now()
        self.has_pose = False
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('Sensor fusion node initialized')

    def pose_callback(self, msg):
        try:
            self.state[0] = msg.pose.position.x
            self.state[1] = msg.pose.position.y
            self.state[2] = 2 * np.arctan2(msg.pose.orientation.z, msg.pose.orientation.w)
            self.has_pose = True
            self.get_logger().info(f'Pose update received: ({self.state[0]}, {self.state[1]}, {self.state[2]})')
        except Exception as e:
            self.get_logger().error(f'Pose callback error: {str(e)}')

    def imu_callback(self, msg):
        try:
            current_time = self.get_clock().now()
            dt = (current_time - self.last_time).nanoseconds / 1e9
            self.last_time = current_time
            self.state[2] += msg.angular_velocity.z * dt  # Update theta
            self.state[3] += msg.linear_acceleration.x * dt  # Update vx
            self.state[4] += msg.linear_acceleration.y * dt  # Update vy
            self.get_logger().info(f'IMU update received: theta={self.state[2]}, vx={self.state[3]}, vy={self.state[4]}')
        except Exception as e:
            self.get_logger().error(f'IMU callback error: {str(e)}')

    def gps_callback(self, msg):
        try:
            # Check if latitude and longitude are reasonable
            if -90 <= msg.latitude <= 90 and -180 <= msg.longitude <= 180:
                self.state[0] = msg.latitude * 111000  # Approx meters per degree latitude
                self.state[1] = msg.longitude * 111000 * np.cos(np.radians(msg.latitude))  # Adjust for longitude
                self.get_logger().info(f'GPS update received: ({self.state[0]}, {self.state[1]})')
            else:
                self.get_logger().warn(f'Invalid GPS data: lat={msg.latitude}, lon={msg.longitude}')
        except Exception as e:
            self.get_logger().error(f'GPS callback error: {str(e)}')

    def timer_callback(self):
        if self.has_pose:  # Only publish if pose is initialized
            self.publish_odometry()

    def publish_odometry(self):
        try:
            odom = Odometry()
            odom.header.stamp = self.get_clock().now().to_msg()
            odom.header.frame_id = 'map'
            odom.child_frame_id = 'base_link'
            odom.pose.pose.position.x = self.state[0]
            odom.pose.pose.position.y = self.state[1]
            odom.pose.pose.orientation.z = np.sin(self.state[2] / 2)
            odom.pose.pose.orientation.w = np.cos(self.state[2] / 2)
            odom.twist.twist.linear.x = self.state[3]
            odom.twist.twist.linear.y = self.state[4]
            self.odom_pub.publish(odom)
            self.get_logger().info(f'Published odometry: ({odom.pose.pose.position.x}, {odom.pose.pose.position.y})')
        except Exception as e:
            self.get_logger().error(f'Publish odometry error: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = SensorFusionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()