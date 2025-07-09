import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
import os

class RCNNLocalizationNode(Node):
    def __init__(self):
        super().__init__('rcnn_localization_node')
        self.subscription = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, 10)
        self.publisher = self.create_publisher(PoseStamped, '/localization/pose', 10)
        self.bridge = CvBridge()
        self.landmark_map = {'stop_sign': (10.0, 0.0)}
        self.debug_dir = '/home/metasebiya/debug_images'
        os.makedirs(self.debug_dir, exist_ok=True)
        self.get_logger().info('Color-based localization initialized')

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            self.get_logger().info('Received camera image')
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            lower_red1 = np.array([0, 30, 10])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([140, 30, 10])
            upper_red2 = np.array([180, 255, 255])
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = cv2.bitwise_or(mask1, mask2)
            red_pixels = cv2.countNonZero(mask)
            self.get_logger().info(f'Red pixels detected: {red_pixels}')
            cv2.imwrite(os.path.join(self.debug_dir, f'mask_{msg.header.stamp.sec}.png'), mask)
            if red_pixels > 5:  # Minimal threshold
                x, y = self.landmark_map['stop_sign']
                pose = PoseStamped()
                pose.header = msg.header
                pose.header.frame_id = 'map'
                pose.pose.position.x = x
                pose.pose.position.y = y
                pose.pose.position.z = 0.0
                pose.pose.orientation.w = 1.0
                self.publisher.publish(pose)
                self.get_logger().info(f'Localized at ({x}, {y}) based on red stop sign detection')
            else:
                self.get_logger().warn('No red stop sign detected')
        except Exception as e:
            self.get_logger().error(f'Error processing image: {str(e)}')

def main(args=None):
    rclpy.init(args=args)
    node = RCNNLocalizationNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()