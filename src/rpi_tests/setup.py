from setuptools import find_packages, setup

package_name = 'rpi_tests'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='deepanshu',
    maintainer_email='deepanshu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [       
            "sub_to_vel = rpi_tests.cmd_vel_to_serial:main",
            "calculate_odometry = rpi_tests.odometry:main",
            "robot_joint_state = rpi_tests.encoder_to_joint_state:main",
            "imu_data = rpi_tests.imu_node:main",
        ],
    },
)
