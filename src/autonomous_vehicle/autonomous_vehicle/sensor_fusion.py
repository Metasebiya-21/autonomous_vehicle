import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, NavSatFix
from nav_msgs.msg import Odometry
import numpy as np
import math

class SensorFusionNode(Node):
    def __init__(self):
        super().__init__('sensor_fusion_node')
        self.imu_sub = self.create_subscription(
            Imu, '/imu/data', self.imu_callback, 10)
        self.gps_sub = self.create_subscription(
            NavSatFix, '/gps/fix', self.gps_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odometry/filtered', 10)
        # Static vehicle at (0, 0, 0.5)
        self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # [x, y, theta, vx, vy]
        # Changed to 6x6 matrix for [x, y, z, roll, pitch, yaw]
        self.covariance = np.eye(6) * 0.1  # 6x6 diagonal matrix
        self.last_time = self.get_clock().now()
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10 Hz
        self.get_logger().info('Sensor fusion node initialized for static vehicle')

    def imu_callback(self, msg):
        try:
            current_time = self.get_clock().now()
            dt = max((current_time - self.last_time).nanoseconds / 1e9, 0.001)
            self.last_time = current_time
            # Handle zeroed IMU covariances
            default_cov = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
            if all(v == 0.0 for v in msg.orientation_covariance):
                msg.orientation_covariance = default_cov
            if all(v == 0.0 for v in msg.angular_velocity_covariance):
                msg.angular_velocity_covariance = default_cov
            if all(v == 0.0 for v in msg.linear_acceleration_covariance):
                msg.linear_acceleration_covariance = default_cov
            # Static vehicle: ignore IMU updates for now
            self.get_logger().debug(f'IMU received: angular_z={msg.angular_velocity.z}, accel_x={msg.linear_acceleration.x}')
        except Exception as e:
            self.get_logger().error(f'IMU callback error: {str(e)}')

    def gps_callback(self, msg):
        try:
            # Static vehicle: ignore GPS for now or validate
            if -90 <= msg.latitude <= 90 and -180 <= msg.longitude <= 180:
                self.get_logger().debug(f'GPS received: lat={msg.latitude}, lon={msg.longitude}')
            else:
                self.get_logger().warn(f'Invalid GPS data: lat={msg.latitude}, lon={msg.longitude}')
        except Exception as e:
            self.get_logger().error(f'GPS callback error: {str(e)}')

    def timer_callback(self):
        self.publish_odometry()

    def publish_odometry(self):
        try:
            odom = Odometry()
            odom.header.stamp = self.get_clock().now().to_msg()
            odom.header.frame_id = 'map'
            odom.child_frame_id = 'base_link'
            odom.pose.pose.position.x = self.state[0]  # 0.0
            odom.pose.pose.position.y = self.state[1]  # 0.0
            odom.pose.pose.position.z = 0.5  # Static z
            # Set orientation for theta (yaw), roll and pitch are 0
            odom.pose.pose.orientation.x = 0.0
            odom.pose.pose.orientation.y = 0.0
            odom.pose.pose.orientation.z = np.sin(self.state[2] / 2)
            odom.pose.pose.orientation.w = np.cos(self.state[2] / 2)
            odom.twist.twist.linear.x = self.state[3]  # 0.0
            odom.twist.twist.linear.y = self.state[4]  # 0.0
            odom.twist.twist.linear.z = 0.0  # Static z velocity
            # Use 6x6 covariance and validate
            odom.pose.covariance = self.covariance.flatten().tolist()
            odom.twist.covariance = self.covariance.flatten().tolist()
            # Check for invalid covariance values
            if any(not isinstance(v, float) or math.isnan(v) or math.isinf(v) for v in odom.pose.covariance):
                self.get_logger().error("Invalid covariance, skipping publish")
                return
            self.odom_pub.publish(odom)
            self.get_logger().info(f'Published odometry: ({odom.pose.pose.position.x}, {odom.pose.pose.position.y}, {odom.pose.pose.position.z})')
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