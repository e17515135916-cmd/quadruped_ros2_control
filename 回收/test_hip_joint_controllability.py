#!/usr/bin/env python3
"""
Test hip joint controllability in Gazebo
Tests that j11, j21, j31, j41 can be controlled and rotate about x-axis
"""

import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from sensor_msgs.msg import JointState
from builtin_interfaces.msg import Duration
import time
import math


class HipJointControllabilityTest(Node):
    def __init__(self):
        super().__init__('hip_joint_controllability_test')
        
        self.publisher = self.create_publisher(
            JointTrajectory,
            '/joint_trajectory_controller/joint_trajectory',
            10
        )
        
        self.joint_state_sub = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # All joints controlled by joint_trajectory_controller
        self.joint_names = [
            'j11', 'j111', 'j1111',    # Leg 1 (front left)
            'j21', 'j211', 'j2111',    # Leg 2 (front right)
            'j31', 'j311', 'j3111',    # Leg 3 (back left)
            'j41', 'j411', 'j4111'     # Leg 4 (back right)
        ]
        
        # Hip joints to test
        self.hip_joints = ['j11', 'j21', 'j31', 'j41']
        
        self.current_joint_states = {}
        self.test_results = []
        
        self.get_logger().info('🐕 Hip Joint Controllability Test')
        self.get_logger().info('Testing hip joints: j11, j21, j31, j41')
        self.get_logger().info('Waiting for joint states...')
        
    def joint_state_callback(self, msg):
        """Store current joint states"""
        for i, name in enumerate(msg.name):
            if name in self.hip_joints:
                self.current_joint_states[name] = msg.position[i]
    
    def send_command(self, positions, duration_sec, description=""):
        """Send joint command"""
        if description:
            self.get_logger().info(f'📤 {description}')
        
        traj = JointTrajectory()
        traj.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start = Duration(sec=duration_sec, nanosec=0)
        
        traj.points = [point]
        self.publisher.publish(traj)
    
    def wait_for_joint_states(self, timeout=5.0):
        """Wait until we have joint states for all hip joints"""
        start_time = time.time()
        while len(self.current_joint_states) < len(self.hip_joints):
            if time.time() - start_time > timeout:
                self.get_logger().error('❌ Timeout waiting for joint states')
                return False
            rclpy.spin_once(self, timeout_sec=0.1)
        return True
    
    def verify_joint_moved(self, joint_name, target_position, tolerance=0.1):
        """Verify that a joint moved to the target position"""
        if joint_name not in self.current_joint_states:
            self.get_logger().error(f'❌ No state for joint {joint_name}')
            return False
        
        current = self.current_joint_states[joint_name]
        error = abs(current - target_position)
        
        if error < tolerance:
            self.get_logger().info(f'✅ {joint_name}: target={target_position:.3f}, current={current:.3f}, error={error:.3f}')
            return True
        else:
            self.get_logger().warn(f'⚠️  {joint_name}: target={target_position:.3f}, current={current:.3f}, error={error:.3f}')
            return False
    
    def run_test(self):
        """Run controllability tests"""
        
        # Wait for initial joint states
        if not self.wait_for_joint_states():
            return
        
        self.get_logger().info('\n=== Initial Joint States ===')
        for joint in self.hip_joints:
            pos = self.current_joint_states.get(joint, 0.0)
            self.get_logger().info(f'{joint}: {pos:.3f} rad')
        
        # Test 1: Move all hip joints to neutral position (0.0)
        self.get_logger().info('\n=== Test 1: Move all hip joints to neutral (0.0) ===')
        neutral = [
            0.0, 0.0, 0.0,  # Leg 1
            0.0, 0.0, 0.0,  # Leg 2
            0.0, 0.0, 0.0,  # Leg 3
            0.0, 0.0, 0.0   # Leg 4
        ]
        self.send_command(neutral, 2, "Moving to neutral position")
        time.sleep(3)
        
        # Verify all hip joints are at 0.0
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)
        
        test1_pass = all(self.verify_joint_moved(joint, 0.0, tolerance=0.1) for joint in self.hip_joints)
        self.test_results.append(('Neutral position', test1_pass))
        
        # Test 2: Move j11 to positive angle (0.5 rad)
        self.get_logger().info('\n=== Test 2: Move j11 to +0.5 rad ===')
        j11_positive = [
            0.5, 0.0, 0.0,  # Leg 1: j11=0.5
            0.0, 0.0, 0.0,  # Leg 2
            0.0, 0.0, 0.0,  # Leg 3
            0.0, 0.0, 0.0   # Leg 4
        ]
        self.send_command(j11_positive, 2, "Moving j11 to +0.5 rad")
        time.sleep(3)
        
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)
        
        test2_pass = self.verify_joint_moved('j11', 0.5, tolerance=0.1)
        self.test_results.append(('j11 positive', test2_pass))
        
        # Test 3: Move j11 to negative angle (-0.5 rad)
        self.get_logger().info('\n=== Test 3: Move j11 to -0.5 rad ===')
        j11_negative = [
            -0.5, 0.0, 0.0,  # Leg 1: j11=-0.5
            0.0, 0.0, 0.0,   # Leg 2
            0.0, 0.0, 0.0,   # Leg 3
            0.0, 0.0, 0.0    # Leg 4
        ]
        self.send_command(j11_negative, 2, "Moving j11 to -0.5 rad")
        time.sleep(3)
        
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)
        
        test3_pass = self.verify_joint_moved('j11', -0.5, tolerance=0.1)
        self.test_results.append(('j11 negative', test3_pass))
        
        # Test 4: Move all hip joints to different positions
        self.get_logger().info('\n=== Test 4: Move all hip joints to different positions ===')
        all_different = [
            0.3, 0.0, 0.0,   # Leg 1: j11=0.3
            -0.3, 0.0, 0.0,  # Leg 2: j21=-0.3
            0.4, 0.0, 0.0,   # Leg 3: j31=0.4
            -0.4, 0.0, 0.0   # Leg 4: j41=-0.4
        ]
        self.send_command(all_different, 2, "Moving all hip joints")
        time.sleep(3)
        
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)
        
        test4_results = [
            self.verify_joint_moved('j11', 0.3, tolerance=0.1),
            self.verify_joint_moved('j21', -0.3, tolerance=0.1),
            self.verify_joint_moved('j31', 0.4, tolerance=0.1),
            self.verify_joint_moved('j41', -0.4, tolerance=0.1)
        ]
        test4_pass = all(test4_results)
        self.test_results.append(('All hip joints different', test4_pass))
        
        # Test 5: Test joint limits (within safe range)
        self.get_logger().info('\n=== Test 5: Test joint limits (±1.0 rad) ===')
        limits_test = [
            1.0, 0.0, 0.0,   # Leg 1: j11=1.0
            -1.0, 0.0, 0.0,  # Leg 2: j21=-1.0
            1.0, 0.0, 0.0,   # Leg 3: j31=1.0
            -1.0, 0.0, 0.0   # Leg 4: j41=-1.0
        ]
        self.send_command(limits_test, 3, "Testing joint limits")
        time.sleep(4)
        
        for _ in range(10):
            rclpy.spin_once(self, timeout_sec=0.1)
        
        test5_results = [
            self.verify_joint_moved('j11', 1.0, tolerance=0.15),
            self.verify_joint_moved('j21', -1.0, tolerance=0.15),
            self.verify_joint_moved('j31', 1.0, tolerance=0.15),
            self.verify_joint_moved('j41', -1.0, tolerance=0.15)
        ]
        test5_pass = all(test5_results)
        self.test_results.append(('Joint limits', test5_pass))
        
        # Return to neutral
        self.get_logger().info('\n=== Returning to neutral ===')
        self.send_command(neutral, 2, "Returning to neutral")
        time.sleep(3)
        
        # Print summary
        self.print_summary()
        
        rclpy.shutdown()
    
    def print_summary(self):
        """Print test summary"""
        self.get_logger().info('\n' + '='*60)
        self.get_logger().info('TEST SUMMARY')
        self.get_logger().info('='*60)
        
        for test_name, passed in self.test_results:
            status = '✅ PASS' if passed else '❌ FAIL'
            self.get_logger().info(f'{status}: {test_name}')
        
        total = len(self.test_results)
        passed = sum(1 for _, p in self.test_results if p)
        
        self.get_logger().info('='*60)
        self.get_logger().info(f'Total: {passed}/{total} tests passed')
        
        if passed == total:
            self.get_logger().info('✅ All hip joints are controllable!')
        else:
            self.get_logger().warn(f'⚠️  {total - passed} test(s) failed')


def main(args=None):
    rclpy.init(args=args)
    node = HipJointControllabilityTest()
    
    # Wait a bit for everything to initialize
    time.sleep(2)
    
    try:
        node.run_test()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
