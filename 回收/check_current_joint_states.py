#!/usr/bin/env python3
"""
Check current joint states to verify all joints are at zero
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateChecker(Node):
    def __init__(self):
        super().__init__('joint_state_checker')
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10)
        self.received = False
        
    def joint_state_callback(self, msg):
        if not self.received:
            self.received = True
            print("\n" + "="*60)
            print("CURRENT JOINT STATES")
            print("="*60)
            
            for name, pos in zip(msg.name, msg.position):
                print(f"{name:10s}: {pos:8.4f} rad ({pos*180/3.14159:7.2f}°)")
            
            print("="*60)
            print("\nExpected: All joints should be at 0.0 rad (0.00°)")
            print("Result: All four legs should point DOWNWARD")
            print("="*60 + "\n")

def main():
    rclpy.init()
    node = JointStateChecker()
    
    print("\nWaiting for joint states...")
    rclpy.spin_once(node, timeout_sec=5.0)
    
    if not node.received:
        print("No joint states received. Is RViz running?")
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
