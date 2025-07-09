import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import Twist
import numpy as np

class SimpleControlNode(Node):
    def __init__(self):
        super().__init__('simple_control_node')
        self.path_sub = self.create_subscription(
            Path, '/path', self.path_callback, 10)
        self.odom_sub = self.create_subscription(
            Odometry, '/odometry/filtered', self.odom_callback, 10)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.path = None
        self.current_pose = None
        self.kp_linear = 0.5
        self.kp_angular = 1.0
        self.get_logger().info('SimpleControlNode initialized')

    def path_callback(self, msg):
        self.path = [(pose.pose.position.x, pose.pose.position.y) for pose in msg.poses]
        self.get_logger().info(f'Received path with {len(self.path)} waypoints')

    def odom_callback(self, msg):
        self.get_logger().info('Received odometry')
        if self.path is None or len(self.path) == 0:
            self.get_logger().warn('No valid path, skipping cmd_vel')
            return
        self.current_pose = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y])
        distances = [np.linalg.norm(self.current_pose - np.array(p)) for p in self.path]
        target_idx = np.argmin(distances)
        target = np.array(self.path[target_idx])
        error = target - self.current_pose
        distance = np.linalg.norm(error)
        angle_to_target = np.arctan2(error[1], error[0])
        current_yaw = 2 * np.arctan2(msg.pose.pose.orientation.z, msg.pose.pose.orientation.w)
        angular_error = angle_to_target - current_yaw
        twist = Twist()
        twist.linear.x = self.kp_linear * distance if distance > 0.1 else 0.0
        twist.angular.z = self.kp_angular * angular_error
        self.cmd_pub.publish(twist)
        self.get_logger().info(f'Published cmd_vel: linear.x={twist.linear.x}, angular.z={twist.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    node = SimpleControlNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()