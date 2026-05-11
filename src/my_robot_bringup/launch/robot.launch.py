from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    ld = LaunchDescription()

    #talker_node = Node(
    #    package= "demo_nodes_cpp",
    #    executable= "talker",
    #    namespace="cpp",
    #    name="my_talker",
    #    remappings=[
    #        ("chatter", "my_chatter")
    #    ]
    #    parameters=(
        #     {"abc":"abs"}
        #     {"sos":"hoh"}
        # )
    #)

    cmd_vel_to_serial_node = Node(
        package="rpi_tests",
        executable="sub_to_vel",
        parameters=[{'use_sim_time': False}],
    )

    odometry_node = Node(
        package="rpi_tests",
        executable="calculate_odometry",
        parameters=[{'use_sim_time': False}],
    )

    imu_node = Node(
        package="rpi_tests",
        executable="imu_data",
        parameters=[{'use_sim_time': False}],
    )

    robot_joint_state_node = Node(
        package="rpi_tests",
        executable="robot_joint_state",
        parameters=[{'use_sim_time': False}]
    )

    rplidar_launch = os.path.join(get_package_share_directory('sllidar_ros2'), 'launch', 'sllidar_a1_launch.py')


    #rplidar_launch = os.path.join(get_package_share_directory('rplidar_ros'), 'launch', 'rplidar.launch.py')

    lidar_node = IncludeLaunchDescription(PythonLaunchDescriptionSource(rplidar_launch))

    
    ld.add_action(robot_joint_state_node)
    ld.add_action(cmd_vel_to_serial_node)
    ld.add_action(odometry_node)
    ld.add_action(imu_node)
    ld.add_action(lidar_node)

    return ld