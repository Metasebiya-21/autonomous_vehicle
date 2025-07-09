import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, NavSatFix, LaserScan
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
        self.lidar_sub = self.create_subscription(
            LaserScan, '/lidar/scan', self.lidar_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, '/odometry/filtered', 10)
        self.state = np.zeros(5)  # [x, y, theta, vx, vy]
        self.covariance = np.eye(5) * 0.1
        self.last_time = self.get_clock().now()

    def pose_callback(self, msg):
        self.state[0] = msg.pose.position.x
        self.state[1] = msg.pose.position.y
        self.state[2] = 2 * np.arctan2(msg.pose.orientation.z, msg.pose.orientation.w)
        self.publish_odometry()

    def imu_callback(self, msg):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time
        self.state[2] += msg.angular_velocity.z * dt
        self.state[3] += msg.linear_acceleration.x * dt
        self.state[4] += msg.linear_acceleration.y * dt
        self.publish_odometry()

    def gps_callback(self, msg):
        self.state[0] = msg.latitude * 111000  # Approx. conversion to meters
        self.state[1] = msg.longitude * 111000 * np.cos(msg.latitude * np.pi / 180)
        self.publish_odometry()

    def lidar_callback(self, msg):
        # Placeholder: Ignore LiDAR for now
        pass

    def publish_odometry(self):
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

def main(args=None):
    rclpy.init(args=args)
    node = SensorFusionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()