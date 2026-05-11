import rclpy
import json
from rclpy.node import Node
from rpi_tests.connect_to_arduino import ArduinoConnection
from geometry_msgs.msg import Twist
from my_robot_interfaces.msg import BaseDriveEncoderData
from my_robot_interfaces.msg import Mpu6050

class CmdVelToSerial(Node):
    def __init__(self):
        super().__init__("cmd_vel_to_serial")
        self.subscribe_ = self.create_subscription(Twist, "/cmd_vel", self.vel_callback, 10)
        self.connect_to_arduino = ArduinoConnection(port='/dev/ttyACM0', logger=self.get_logger())
        self.ser = self.connect_to_arduino.ser
        self.base_drive_data_pub = self.create_publisher(BaseDriveEncoderData, "base_drive_encoder_data", 10)
        self.imu_data_pub = self.create_publisher(Mpu6050, "imu_data", 10)
        self.read_and_pub_timer_ = self.create_timer(0.02, self.read_and_publish)
        self.get_logger().info("Subscribing to cmd_vel topic.")

    def vel_callback(self, msg: Twist):
        data = {
            "linear": msg.linear.x,
            "angular": msg.angular.z
        }
        json_data = json.dumps(data) + "\n"
        self.ser.write(json_data.encode('utf-8'))
        self.get_logger().info(f"cmd_vel sent to arduino: {json_data.strip()}")

    def read_and_publish(self):
        line = self.connect_to_arduino.readline()

        if line is None:
            self.connect_to_arduino.connect()
            return

        if not line:
            self.get_logger().debug("No data received from Arduino (timeout or idle)")
            return
        
        try:
            raw_data = line.decode('utf-8').rstrip()
            if not raw_data:
                self.get_logger().warn("Received empty raw_data from serial")
                return

            self.get_logger().debug(f"Raw data received: {raw_data}")
            
            data = json.loads(raw_data)
            drive_base_data = BaseDriveEncoderData()
            imu_data = Mpu6050()
            if not data:
                self.get_logger().warn("Parsed JSON is empty")
                drive_base_data.right_encoder_ticks = "0"
                drive_base_data.left_encoder_ticks = "0"
                drive_base_data.header.stamp = self.get_clock().now().to_msg()
                imu_data.gyro_x = "0.0"
                imu_data.gyro_y = "0.0"
                imu_data.gyro_z = "0.0"
                imu_data.accel_x = "0.0"
                imu_data.accel_y = "0.0"
                imu_data.accel_z = "0.0"
            else:
                drive_base_data.left_encoder_ticks = int(data["lticks"])
                drive_base_data.right_encoder_ticks = int(data["rticks"])
                drive_base_data.header.stamp = self.get_clock().now().to_msg()
                imu_data.gyro_x = float(data["gyro_x"])
                imu_data.gyro_y = float(data["gyro_y"])
                imu_data.gyro_z = float(data["gyro_z"])
                imu_data.accel_x = float(data["accel_x"])
                imu_data.accel_y = float(data["accel_y"])
                imu_data.accel_z = float(data["accel_z"])
                self.get_logger().debug(f"Parsed ticks -> Left encoder: {drive_base_data.left_encoder_ticks}," 
                                        f"Right encoder: {drive_base_data.right_encoder_ticks},"
                                        f"Gyro_x_val : {imu_data.gyro_x},"
                                        f"Gyro_y_val : {imu_data.gyro_y},"
                                        f"Gyro_z_val : {imu_data.gyro_z},"
                                        f"Accel_x_val : {imu_data.accel_x},"
                                        f"Accel_y_val : {imu_data.accel_y},"
                                        f"Accel_z_val : {imu_data.accel_z}")
            
            self.base_drive_data_pub.publish(drive_base_data) 
            self.imu_data_pub.publish(imu_data)
                
        except Exception as e:
            self.get_logger().warn(f"Invalid data error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelToSerial()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()