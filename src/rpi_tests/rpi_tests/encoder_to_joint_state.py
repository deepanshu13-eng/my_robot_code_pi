import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from my_robot_interfaces.msg import BaseDriveEncoderData
import math

TICKS_PER_REV = 420  

class EncoderToJointState(Node):

    def __init__(self):
        super().__init__('encoder_to_joint_state')
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.subscription = self.create_subscription(BaseDriveEncoderData, '/base_drive_encoder_data', self.callback, 10)

        self.left_encoder_ticks = 0
        self.right_encoder_ticks = 0
        self.get_logger().info("Joint state node started...")

    def callback(self, msg):
        self.left_encoder_ticks = msg.left_encoder_ticks
        self.right_encoder_ticks = msg.right_encoder_ticks

        left_angle = self.left_encoder_ticks * (2 * math.pi / TICKS_PER_REV)
        right_angle = -(self.right_encoder_ticks * (2 * math.pi / TICKS_PER_REV))

        joint_msg = JointState()
        joint_msg.header.stamp = self.get_clock().now().to_msg()
        joint_msg.header.frame_id = "base_link"

        joint_msg.name = [
            'front_base_left_wheel_joint',
            'front_base_right_wheel_joint',
            'rear_base_left_wheel_joint',
            'rear_base_right_wheel_joint',
        ]

        joint_msg.position = [left_angle, right_angle, left_angle, right_angle]
        self.publisher.publish(joint_msg)

def main():
    rclpy.init()
    node = EncoderToJointState()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()