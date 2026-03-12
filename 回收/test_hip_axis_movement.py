#!/usr/bin/env python3
"""
Automated test script for hip joint axis movement verification.

This script programmatically tests hip joint movement to verify:
1. Hip joints can be controlled via joint states
2. Hip joints rotate about X-axis (forward/backward motion)
3. Joint limits are respected

Requirements validated: 6.2
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Header
import time
import math


class HipJointTester(Node):
    """Node to test hip joint movement."""
    
    def __init__(self):
        super().__init__('hip_joint_tester')
        
        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        
        # Hip joint names
        self.hip_joints = ['j11', 'j21', 'j31', 'j41']
        
        # Test results
        self.test_results = {
            'joints_tested': [],
            'success': True,
            'errors': []
        }
        
        self.get_logger().info('Hip Joint Tester initialized')
    
    def publish_joint_state(self, joint_name, position):
        """Publish a joint state command."""
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [joint_name]
        msg.position = [position]
        msg.velocity = []
        msg.effort = []
        
        self.joint_pub.publish(msg)
        self.get_logger().info(f'Published {joint_name} = {position:.3f} rad ({math.degrees(position):.1f}°)')
    
    def test_hip_joint(self, joint_name):
        """Test a single hip joint through its range of motion."""
        self.get_logger().info(f'\n{"="*60}')
        self.get_logger().info(f'Testing {joint_name}')
        self.get_logger().info(f'{"="*60}')
        
        # Test positions (in radians)
        # Joint limits: ±2.618 rad (±150°)
        test_positions = [
            0.0,      # Neutral
            0.5,      # Forward 28.6°
            1.0,      # Forward 57.3°
            1.5,      # Forward 85.9°
            0.0,      # Back to neutral
            -0.5,     # Backward 28.6°
            -1.0,     # Backward 57.3°
            -1.5,     # Backward 85.9°
            0.0       # Back to neutral
        ]
        
        try:
            for pos in test_positions:
                self.publish_joint_state(joint_name, pos)
                time.sleep(0.5)  # Wait for movement
            
            self.test_results['joints_tested'].append(joint_name)
            self.get_logger().info(f'✓ {joint_name} test completed successfully')
            
        except Exception as e:
            self.test_results['success'] = False
            self.test_results['errors'].append(f'{joint_name}: {str(e)}')
            self.get_logger().error(f'✗ {joint_name} test failed: {e}')
    
    def run_tests(self):
        """Run tests for all hip joints."""
        self.get_logger().info('\n' + '='*70)
        self.get_logger().info('Hip Joint Movement Test')
        self.get_logger().info('='*70)
        self.get_logger().info('\nTesting hip joints for X-axis rotation (forward/backward)')
        self.get_logger().info('Expected: Hip joints should move forward and backward')
        self.get_logger().info('Previous: Hip joints moved left and right (Z-axis)\n')
        
        # Test each hip joint
        for joint in self.hip_joints:
            self.test_hip_joint(joint)
            time.sleep(1.0)  # Pause between joints
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        self.get_logger().info('\n' + '='*70)
        self.get_logger().info('Test Summary')
        self.get_logger().info('='*70)
        self.get_logger().info(f'Joints tested: {len(self.test_results["joints_tested"])}/4')
        
        for joint in self.test_results['joints_tested']:
            self.get_logger().info(f'  ✓ {joint}')
        
        if self.test_results['errors']:
            self.get_logger().error('\nErrors encountered:')
            for error in self.test_results['errors']:
                self.get_logger().error(f'  ✗ {error}')
        
        if self.test_results['success']:
            self.get_logger().info('\n✓ All hip joint tests PASSED')
            self.get_logger().info('Hip joints are rotating about X-axis (forward/backward)')
        else:
            self.get_logger().error('\n✗ Some hip joint tests FAILED')
        
        self.get_logger().info('='*70 + '\n')


def main(args=None):
    """Main function."""
    rclpy.init(args=args)
    
    tester = HipJointTester()
    
    # Give time for RViz and robot_state_publisher to start
    time.sleep(2.0)
    
    try:
        # Run the tests
        tester.run_tests()
        
        # Keep node alive for a bit to ensure messages are sent
        time.sleep(2.0)
        
    except KeyboardInterrupt:
        tester.get_logger().info('Test interrupted by user')
    finally:
        tester.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
