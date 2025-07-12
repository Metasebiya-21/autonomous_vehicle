import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import PoseStamped
import numpy as np

class PathPlanningNode(Node):
    def __init__(self):
        super().__init__('path_planning_node')
        qos = rclpy.qos.QoSProfile(depth=10, reliability=rclpy.qos.ReliabilityPolicy.RELIABLE)
        self.odom_sub = self.create_subscription(
            Odometry, '/odometry/filtered', self.odom_callback, qos)
        self.loc_sub = self.create_subscription(
            PoseStamped, '/localization/pose', self.loc_callback, qos)
        self.path_pub = self.create_publisher(Path, '/path', qos)
        self.current_pose = None
        self.stop_sign_pose = None
        self.goal = np.array([20.0, 10.0])
        self.get_logger().info('Path planning node initialized')

    def odom_callback(self, msg):
        self.current_pose = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y])
        self.get_logger().debug(f'Received odometry: {self.current_pose}')
        path = self.plan_path()
        self.publish_path(path)

    def loc_callback(self, msg):
        self.stop_sign_pose = np.array([msg.pose.position.x, msg.pose.position.y])
        self.get_logger().info(f'Received stop sign pose: {self.stop_sign_pose}')
        path = self.plan_path()
        self.publish_path(path)

    def plan_path(self):
        if self.current_pose is None:
            self.get_logger().warn('No odometry data, cannot plan path')
            return []
        path = []
        steps = 5  # Steps per segment
        start = self.current_pose
        if self.stop_sign_pose is not None:
            stop_sign = self.stop_sign_pose
            for t in range(steps + 1):
                point = start + (stop_sign - start) * t / steps
                path.append(point)
            for t in range(1, steps + 1):
                point = stop_sign + (self.goal - stop_sign) * t / steps
                path.append(point)
            self.get_logger().info(f'Planned path via stop sign: {stop_sign}')
        else:
            for t in range(steps + 1):
                point = start + (self.goal - start) * t / steps
                path.append(point)
            self.get_logger().info('No stop sign detected, planned direct path to goal')
        return path

    def publish_path(self, path_points):
        if not path_points:
            self.get_logger().warn('No path points to publish')
            return
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'map'
        for x, y in path_points:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = float(x)
            pose.pose.position.y = float(y)
            pose.pose.position.z = 0.0
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.get_logger().info(f'Publishing path with {len(path.poses)} poses')
        self.path_pub.publish(path)

def main(args=None):
    rclpy.init(args=args)
    node = PathPlanningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()