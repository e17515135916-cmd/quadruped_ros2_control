#!/usr/bin/env python3
"""
Test script to verify all four legs point downward at zero angles
After fixing hip_axis for rear legs
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import time

class LegOrientationTest(Node):
    def __init__(self):
        super().__init__('leg_orientation_test')
        self.publisher = self.create_publisher(JointState, '/joint_states', 10)
        
    def set_all_joints_zero(self):
        """Set all joints to zero position"""
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        
        # All joints to zero
        msg.name = [
            'j1', 'j11', 'j111',    # Leg 1
            'j2', 'j21', 'j211',    # Leg 2
            'j3', 'j31', 'j311',    # Leg 3
            'j4', 'j41', 'j411'     # Leg 4
        ]
        msg.position = [0.0] * 12
        
        self.get_logger().info('Setting all joints to zero position...')
        self.get_logger().info('All four legs should now point downward (dog-style)')
        
        # Publish multiple times to ensure it's received
        for _ in range(10):
            self.publisher.publish(msg)
            time.sleep(0.1)

def main():
    rclpy.init()
    node = LegOrientationTest()
    
    print("\n" + "="*60)
    print("LEG ORIENTATION TEST - After hip_axis Fix")
    print("="*60)
    print("\nThis test sets all joints to zero position.")
    print("Expected result: All four legs point DOWNWARD (dog-style)")
    print("\nPrevious issue: Rear legs pointed in wrong direction")
    print("Fix applied: Changed hip_axis from '-1 0 0' to '1 0 0' for rear legs")
    print("="*60 + "\n")
    
    time.sleep(2)
    node.set_all_joints_zero()
    time.sleep(2)
    
    print("\n" + "="*60)
    print("Test complete. Check RViz visualization:")
    print("- All four legs should point downward")
    print("- Legs should be parallel to each other")
    print("- Configuration should look like a dog, not a spider")
    print("="*60 + "\n")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
