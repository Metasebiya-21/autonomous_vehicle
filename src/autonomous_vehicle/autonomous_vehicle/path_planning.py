import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path, Odometry  # Added Odometry import
from geometry_msgs.msg import PoseStamped
import numpy as np

class PathPlanningNode(Node):
    def __init__(self):
        super().__init__('path_planning_node')
        self.odom_sub = self.create_subscription(
            Odometry, '/odometry/filtered', self.odom_callback, 10)
        self.path_pub = self.create_publisher(Path, '/path', 10)
        self.current_pose = None
        self.goal = np.array([20.0, 10.0])

    def odom_callback(self, msg):
        self.current_pose = np.array([msg.pose.pose.position.x, msg.pose.pose.position.y])
        path = self.plan_path()
        self.publish_path(path)

    def plan_path(self):
        # Simple straight-line path
        start = self.current_pose
        goal = self.goal
        steps = 10
        path = [start + (goal - start) * t / steps for t in range(steps + 1)]
        return path

    def publish_path(self, path_points):
        path = Path()
        path.header.stamp = self.get_clock().now().to_msg()
        path.header.frame_id = 'map'
        for x, y in path_points:
            pose = PoseStamped()
            pose.header = path.header
            pose.pose.position.x = x
            pose.pose.position.y = y
            pose.pose.orientation.w = 1.0
            path.poses.append(pose)
        self.path_pub.publish(path)

def main(args=None):
    rclpy.init(args=args)
    node = PathPlanningNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()