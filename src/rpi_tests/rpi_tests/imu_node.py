import rclpy
from rclpy.node import Node
import json
from my_robot_interfaces.msg import Mpu6050
from sensor_msgs.msg import Imu

class IMUNode(Node):

    def __init__(self):
        super().__init__('imu_node')
        self.create_subscription(Mpu6050, '/imu_data', self.imu_callback, 10)
        self.imu_pub = self.create_publisher(Imu, '/imu', 20)
        self.latest_msg = None   # 🔥 store latest gyro data

        self.create_timer(0.02, self.publish_imu)  # 50 Hz
        self.get_logger().info("Imu node has started...")

    # -------- Store data only --------
    def imu_callback(self, msg):
        self.latest_msg = msg


    def publish_imu(self):
        if self.latest_msg is None:
            return

        msg = self.latest_msg

        imu_msg = Imu()
        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = "imu_link"

        # =====================================
        # Linear acceleration (m/s²)
        # =====================================

        imu_msg.linear_acceleration.x = float(msg.accel_x)
        imu_msg.linear_acceleration.y = float(msg.accel_y)
        imu_msg.linear_acceleration.z = float(msg.accel_z)

        # =====================================
        # Angular velocity (rad/s)
        # Already converted in Arduino
        # =====================================

        imu_msg.angular_velocity.x = float(msg.gyro_x)
        imu_msg.angular_velocity.y = float(msg.gyro_y)
        imu_msg.angular_velocity.z = float(msg.gyro_z)

        # =====================================
        # Orientation unavailable
        # =====================================

        imu_msg.orientation_covariance[0] = -1.0

        # =====================================
        # Covariances
        # =====================================

        imu_msg.angular_velocity_covariance = [
            0.02, 0.0, 0.0,
            0.0, 0.02, 0.0,
            0.0, 0.0, 0.02
        ]

        imu_msg.linear_acceleration_covariance = [
            0.04, 0.0, 0.0,
            0.0, 0.04, 0.0,
            0.0, 0.0, 0.04
        ]

        self.imu_pub.publish(imu_msg)


def main(args=None):
    rclpy.init(args=args)
    node = IMUNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()