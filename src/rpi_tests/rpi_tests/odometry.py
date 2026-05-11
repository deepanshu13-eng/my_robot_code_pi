import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math

from my_robot_interfaces.msg import BaseDriveEncoderData


class EncoderOdometry(Node):
    def __init__(self):
        super().__init__('encoder_odometry')

        # -------- Robot Parameters --------
        self.wheel_radius = 0.055
        self.wheel_base = 0.28
        self.ticks_per_rev = 420

        self.tick_to_meter = (2 * math.pi * self.wheel_radius) / self.ticks_per_rev

        # -------- Robot State --------
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0

        self.prev_left = None
        self.prev_right = None
        self.prev_time = None

        self.latest_msg = None   # 🔥 store latest encoder data

        # -------- ROS Interfaces --------
        self.odom_pub = self.create_publisher(Odometry, '/odom', 20)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(
            BaseDriveEncoderData,
            '/base_drive_encoder_data',
            self.encoder_callback,
            20
        )

        # 🔥 Timer = stable odometry rate
        self.create_timer(0.033, self.publish_odom)   # ~30 Hz

        self.get_logger().info("Odometry node has started...")

    # -------- Store data only --------
    def encoder_callback(self, msg):
        self.latest_msg = msg

    # -------- Timer-based publishing --------
    def publish_odom(self):

        if self.latest_msg is None:
            return

        msg = self.latest_msg
        now_ros = self.get_clock().now().to_msg()

        # First message init
        if self.prev_time is None:
            self.prev_time = now_ros
            self.prev_left = msg.left_encoder_ticks
            self.prev_right = msg.right_encoder_ticks
            return

        # -------- Compute dt --------
        dt = (now_ros.sec - self.prev_time.sec) + \
             (now_ros.nanosec - self.prev_time.nanosec) * 1e-9

        if dt <= 0:
            return

        # -------- Tick difference --------
        d_left_ticks = msg.left_encoder_ticks - self.prev_left
        d_right_ticks = -(msg.right_encoder_ticks - self.prev_right)

        self.prev_left = msg.left_encoder_ticks
        self.prev_right = msg.right_encoder_ticks
        self.prev_time = now_ros

        # -------- Calibration --------
        #RIGHT_SCALE = 1.08
        RIGHT_SCALE = 1.00
        d_right_ticks *= RIGHT_SCALE

        # -------- Convert ticks → distance --------
        dist_left = d_left_ticks * self.tick_to_meter
        dist_right = d_right_ticks * self.tick_to_meter

        dist = (dist_left + dist_right) / 2.0
        dtheta = (dist_right - dist_left) / self.wheel_base

        # -------- Pose Update --------
        if abs(dtheta) < 1e-6:
            self.x += dist * math.cos(self.theta)
            self.y += dist * math.sin(self.theta)
        else:
            R = dist / dtheta
            self.x += R * (math.sin(self.theta + dtheta) - math.sin(self.theta))
            self.y -= R * (math.cos(self.theta + dtheta) - math.cos(self.theta))

        self.theta += dtheta
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

        # -------- Velocities --------
        vx = dist / dt
        vth = dtheta / dt

        # -------- Proper Timestamp --------
        now = self.get_clock().now().to_msg()
        #delay = rclpy.time.Duration(seconds=0.0)
        #current_time = current_time - delay
        #now = current_time.to_msg()

        # -------- TF --------
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = "odom"
        t.child_frame_id = "base_footprint"

        t.transform.translation.x = self.x
        t.transform.translation.y = self.y

        qz = math.sin(self.theta / 2.0)
        qw = math.cos(self.theta / 2.0)

        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(t)

        # -------- Odom --------
        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_footprint"

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.twist.twist.linear.x = vx
        odom.twist.twist.angular.z = vth

         # Pose covariance
        odom.pose.covariance[0] = 0.05    # x
        odom.pose.covariance[7] = 0.05    # y
        odom.pose.covariance[35] = 0.1    # yaw

        # Twist covariance
        odom.twist.covariance[0] = 0.02   # vx
        odom.twist.covariance[35] = 0.05  # vth

        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = EncoderOdometry()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()