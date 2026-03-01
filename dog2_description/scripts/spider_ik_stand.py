#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import math
import numpy as np
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration

class SpiderIKStandNode(Node):
    def __init__(self):
        super().__init__('spider_ik_stand_node')
        
        # Publishers for leg joints and rails
        self.joint_pub = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        self.rail_pub = self.create_publisher(
            JointTrajectory,
            '/rail_position_controller/joint_trajectory',
            10
        )
        
        self.joint_names = [
            'lf_haa_joint', 'lf_hfe_joint', 'lf_kfe_joint',
            'rf_haa_joint', 'rf_hfe_joint', 'rf_kfe_joint',
            'lh_haa_joint', 'lh_hfe_joint', 'lh_kfe_joint',
            'rh_haa_joint', 'rh_hfe_joint', 'rh_kfe_joint'
        ]
        self.rail_names = ['j1', 'j2', 'j3', 'j4']
        
        # Robot dimensions (m) - matching URDF
        self.L1 = 0.20  # Upper leg
        self.L2 = 0.20  # Lower leg
        
        # Hip mounting points relative to base_link (simplified/representative)
        # In URDF, these are offset by rails.
        self.hip_offsets = {
            'lf': [1.1026, -0.80953, 0.2649],
            'rf': [1.1071, -0.68953, 0.2649],
            'lh': [1.3491, -0.80953, 0.2649],
            'rh': [1.3491, -0.68953, 0.2649]
        }
        
        # Target foot positions relative to base_link (Spider Stance)
        # Wider and lower for stability
        self.target_height = 0.15 # Height of base above feet
        self.target_spread = 0.35 # Distance from hip to foot in X-Y plane
        
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.sent = False

    def solve_ik(self, dx, dy, dz):
        """
        Solve 3R IK for spider leg (HAA, HFE, KFE)
        dx, dy, dz are target foot positions relative to the HIP joint center.
        """
        # HAA (Yaw) - horizontal plane
        haa = math.atan2(dy, dx)
        
        # Radial distance in horizontal plane
        r = math.sqrt(dx**2 + dy**2)
        
        # Planar 2R solve (HFE, KFE) in the rotated vertical plane
        d_sq = r**2 + dz**2
        d = math.sqrt(d_sq)
        
        # Law of cosines for KFE
        # cos(pi - kfe) = (L1^2 + L2^2 - d^2) / (2 * L1 * L2)
        cos_kfe_inner = (self.L1**2 + self.L2**2 - d_sq) / (2 * self.L1 * self.L2)
        cos_kfe_inner = max(-1.0, min(1.0, cos_kfe_inner))
        # In spider stance, kfe is usually a large positive value (bending down)
        kfe = math.pi - math.acos(cos_kfe_inner)
        
        # Angle of the vector to the target in the radial-Z plane
        alpha = math.atan2(dz, r)
        # Angle within the triangle at the HFE joint
        cos_beta = (self.L1**2 + d_sq - self.L2**2) / (2 * self.L1 * d)
        cos_beta = max(-1.0, min(1.0, cos_beta))
        beta = math.acos(cos_beta)
        
        # HFE = alpha - beta might result in a very low leg. 
        # For spider stance, we often want the knee "up", so HFE is more positive.
        hfe = alpha + beta 
        
        return haa, hfe, kfe

    def timer_callback(self):
        if self.sent:
            return
            
        self.get_logger().info('Calculating Spider IK for standing pose...')
        
        # LF (Front Left)
        haa_lf, hfe_lf, kfe_lf = self.solve_ik(0.2, -0.2, -self.target_height)
        
        # RF (Front Right) - Mirrored logic
        # In your URDF, RF has rpy="1.57 0 0" but different hip_xyz
        haa_rf, hfe_rf, kfe_rf = self.solve_ik(0.2, 0.2, -self.target_height)
        
        # LH (Hind Left)
        haa_lh, hfe_lh, kfe_lh = self.solve_ik(-0.2, -0.2, -self.target_height)
        
        # RH (Hind Right)
        haa_rh, hfe_rh, kfe_rh = self.solve_ik(-0.2, 0.2, -self.target_height)
        
        # Adapt signs for the mirrored coordinate systems
        # LF (Front Left): rpy="1.57 0 0", axis="-1 0 0" -> Positive HAA is out
        # RF (Front Right): rpy="1.57 0 -3.14", axis="-1 0 0" -> Positive HAA is out
        # LH (Hind Left): rpy="1.57 0 0", axis="-1 0 0" -> Positive HAA is out
        # RH (Hind Right): rpy="1.57 0 -3.14", axis="-1 0 0" -> Positive HAA is out
        
        # Based on the mirrored coordinate system (Roll 90), 
        # let's apply the calculated angles to the JointTrajectory.
        
        standing_positions = [
            haa_lf, hfe_lf, kfe_lf,  # LF
            haa_rf, hfe_rf, kfe_rf,  # RF
            haa_lh, hfe_lh, kfe_lh,  # LH
            haa_rh, hfe_rh, kfe_rh   # RH
        ]
        
        # Publish Leg Trajectory
        jt = JointTrajectory()
        jt.joint_names = self.joint_names
        p = JointTrajectoryPoint()
        p.positions = standing_positions
        p.time_from_start = Duration(sec=3, nanosec=0)
        jt.points = [p]
        self.joint_pub.publish(jt)
        
        # Lock Rails at 0.0
        rt = JointTrajectory()
        rt.joint_names = self.rail_names
        rp = JointTrajectoryPoint()
        rp.positions = [0.0, 0.0, 0.0, 0.0]
        rp.time_from_start = Duration(sec=1, nanosec=0)
        rt.points = [rp]
        self.rail_pub.publish(rt)
        
        self.get_logger().info('✅ IK-based stand command published.')
        self.sent = True

def main(args=None):
    rclpy.init(args=args)
    node = SpiderIKStandNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
