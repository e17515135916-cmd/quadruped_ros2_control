#!/usr/bin/env python3

import time

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class SpiderJointSmokeTest(Node):
    def __init__(self):
        super().__init__('spider_joint_smoke_test')

        self.leg_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10,
        )
        self.rail_pub = self.create_publisher(
            JointTrajectory,
            '/rail_position_controller/joint_trajectory',
            10,
        )

        self.leg_joints = [
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint',
        ]
        self.rail_joints = ['j1', 'j2', 'j3', 'j4']

    def send(self):
        # Phase A: neutral leg pose + rail lock at zero
        self._publish_leg([0.0] * 12, sec=2)
        self._publish_rail([0.0, 0.0, 0.0, 0.0], sec=2)
        self.get_logger().info('Published neutral pose')
        time.sleep(2.5)

        # Phase B: spider-like stance
        stance = [0.0, 0.6, 1.2] * 4
        self._publish_leg(stance, sec=3)
        self._publish_rail([-0.03, 0.03, -0.03, 0.03], sec=3)
        self.get_logger().info('Published spider stance + rail motion')
        time.sleep(3.5)

        # Phase C: return safe
        self._publish_leg([0.0] * 12, sec=3)
        self._publish_rail([0.0, 0.0, 0.0, 0.0], sec=3)
        self.get_logger().info('Published return-to-neutral')

    def _publish_leg(self, positions, sec):
        msg = JointTrajectory()
        msg.joint_names = self.leg_joints
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=sec)
        msg.points = [point]
        self.leg_pub.publish(msg)

    def _publish_rail(self, positions, sec):
        msg = JointTrajectory()
        msg.joint_names = self.rail_joints
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=sec)
        msg.points = [point]
        self.rail_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SpiderJointSmokeTest()
    try:
        time.sleep(1.0)
        node.send()
        time.sleep(1.0)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
